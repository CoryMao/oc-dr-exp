#!/usr/bin/env python3
"""
Action Memory 检索工具

v2 — 新增双语检索支持：
  - bm25 (默认): 全文检索 (outcome+target+summary_en+keywords)
  - summary_bm25: 仅检索英文摘要字段 (summary_en + keywords)，纯英文对英文，得分高
  - hybrid: 全文 BM25 + 英文摘要 BM25 加权合并 → 兼顾中文匹配和英文关键词匹配
  - tfidf: 传统 TF-IDF

用法:
  # 全文 BM25（默认）
  python3 retrieve.py --query "MLLM perspective benchmark"

  # 纯英文字段检索（推荐英文 query）
  python3 retrieve.py --query "MLLM perspective benchmark" --method summary_bm25

  # 混合模式（最佳）
  python3 retrieve.py --query "MLLM perspective benchmark" --method hybrid

  # 按 action_type 过滤
  python3 retrieve.py --query "cross scene reasoning" --action-type fetch_paper --show-report

  # 只查失败经验
  python3 retrieve.py --query "404 fetch blocked" --only-failure

  # 记录检索日志
  python3 retrieve.py --query "abstract visual reasoning" --log-retrieve --show-report

  # JSON 输出（便于程序消费）
  python3 retrieve.py --query "binding affinity" --json-output
"""

import json
import math
import sys
import re
import os
from collections import Counter

# ─── 路径（从配置文件读取） ─────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "action_memory_config.json")
_default_memory = os.path.join(os.path.dirname(__file__), "action_memory.jsonl")
_default_retrieve_log = os.path.join(os.path.dirname(__file__), "retrieve_log.jsonl")


def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "enable": True,
            "memory_file": _default_memory,
            "default_top_k": 3,
            "injection": {
                "max_experiences_to_inject": 2,
                "inject_success_too": True,
                "inject_failures_too": True,
            },
        }
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {"enable": False}


_config = _load_config()
MEMORY_FILE = _config.get("memory_file", _default_memory)
if not os.path.isabs(MEMORY_FILE):
    MEMORY_FILE = os.path.join(os.path.dirname(__file__), MEMORY_FILE)

DEFAULT_TOP_K = _config.get("default_top_k", 3)

# ─── 检索日志写入 ─────────────────────────────
def _log_retrieve(query, method, top_k, action_type_filter, only_success, only_failure,
                  results, config_snapshot):
    log_dir = os.path.dirname(_default_retrieve_log) or "."
    os.makedirs(log_dir, exist_ok=True)
    entry = {
        "timestamp": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
        ).isoformat(timespec="seconds"),
        "query": query,
        "method": method,
        "top_k": top_k,
        "action_type_filter": action_type_filter,
        "only_success": only_success,
        "only_failure": only_failure,
        "num_results": len(results),
        "results": results,
        "config": config_snapshot,
    }
    with open(_default_retrieve_log, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── 读取 JSONL ────────────────────────────────
def load_records():
    if not os.path.exists(MEMORY_FILE):
        return []
    records = []
    with open(MEMORY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


# ─── 中文 tokenizer ─────────────────────────────
_CHINESE_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")
_EN_WORD_RE = re.compile(r"[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*")
_SPECIAL_TOKENS = re.compile(r"arxiv|doi|pdf|html|http|https|doi\.org|bioRxiv")


def tokenize(text):
    """中文：char-level + bigram；英文：word-level"""
    text = text.lower()
    tokens = []

    for m in _SPECIAL_TOKENS.finditer(text):
        tokens.append(m.group())
    text_no_special = _SPECIAL_TOKENS.sub(" ", text)

    i = 0
    parts = []
    current = ""
    in_chinese = None
    while i < len(text_no_special):
        ch = text_no_special[i]
        if _CHINESE_RE.match(ch):
            if in_chinese is False and current:
                parts.append(("en", current))
                current = ""
            in_chinese = True
            current += ch
        elif ch.isascii() and (ch.isalnum() or ch == "_"):
            if in_chinese is True and current:
                parts.append(("zh", current))
                current = ""
            in_chinese = False
            current += ch
        else:
            if current:
                parts.append(("zh" if in_chinese else "en", current))
                current = ""
            in_chinese = None
        i += 1
    if current:
        parts.append(("zh" if in_chinese else "en", current))

    for kind, part in parts:
        if kind == "zh":
            for ch in part:
                tokens.append(ch)
            for j in range(len(part) - 1):
                tokens.append(part[j : j + 2])
        else:
            for m in _EN_WORD_RE.finditer(part):
                tokens.append(m.group())

    return tokens


# ─── BM25 ──────────────────────────────────────
class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = [tokenize(doc) for doc in corpus]
        self.n_docs = len(self.corpus)
        self.avg_dl = sum(len(d) for d in self.corpus) / max(self.n_docs, 1)
        self.df = Counter()
        for doc_tokens in self.corpus:
            for t in set(doc_tokens):
                self.df[t] += 1

    def score(self, query_terms, doc_id):
        doc_tokens = self.corpus[doc_id]
        dl = len(doc_tokens)
        score = 0.0
        for qt in set(query_terms):
            if qt not in self.df:
                continue
            idf = math.log(
                (self.n_docs - self.df[qt] + 0.5) / (self.df[qt] + 0.5) + 1.0
            )
            tf = doc_tokens.count(qt)
            score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl))
        return score

    def search(self, query, top_k=3):
        query_terms = tokenize(query)
        if not query_terms:
            return []
        scored = [(self.score(query_terms, i), i) for i in range(self.n_docs)]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [{"score": s, "idx": i} for s, i in scored[:top_k] if s > 0]


# ─── TF-IDF ────────────────────────────────────
class TFIDF:
    def __init__(self, corpus):
        self.corpus = [tokenize(doc) for doc in corpus]
        self.n_docs = len(self.corpus)
        self.df = Counter()
        for doc_tokens in self.corpus:
            for t in set(doc_tokens):
                self.df[t] += 1

    def _tfidf(self, terms, doc_tokens):
        scores = {}
        dl = len(doc_tokens)
        for t in set(terms):
            if t not in self.df:
                continue
            tf = doc_tokens.count(t) / max(dl, 1)
            idf = math.log((self.n_docs + 1) / (self.df[t] + 1) + 1)
            scores[t] = tf * idf
        return sum(scores.values())

    def search(self, query, top_k=3):
        query_terms = tokenize(query)
        if not query_terms:
            return []
        scored = [(self._tfidf(query_terms, self.corpus[i]), i) for i in range(self.n_docs)]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [{"score": s, "idx": i} for s, i in scored[:top_k] if s > 0]


# ─── 构造检索文本 ─────────────────────────────
def _build_doc(rec):
    """将一条记录转为全文本检索（含 summary_en 和 keywords）"""
    parts = [
        rec.get("action_type", ""),
        rec.get("target", "") or "",
        rec.get("outcome", "") or "",
        rec.get("context", "") or "",
        rec.get("error_reason", "") or "",
        rec.get("error_type", "") or "",
        rec.get("summary_en", "") or "",         # ← 新增：英文摘要
        " ".join(rec.get("keywords", [])),        # ← 新增：英文关键词列表
        f"case_id:{rec.get('case_id','')}",
    ]
    return " ".join(parts)


def _build_en_doc(rec):
    """只从英文短字段(summary_en + keywords + target)构建紧凑检索文本"""
    parts = [
        rec.get("summary_en", "") or "",
        " ".join(rec.get("keywords", [])),
        rec.get("target", "") or "",
    ]
    return " ".join(parts)


# ─── 格式化输出 ────────────────────────────────
def _format_outcomes(formatted_results, show_detail):
    lines = []
    for i, r in enumerate(formatted_results):
        tag = "✗" if r.get("success") is False else "✓"
        line = f"  [{i+1}] score={r['score']:.4f}  [{r['case_id']}:step{r['step']}] {tag} {r['action_type']}"
        lines.append(line)
        if show_detail:
            outcome = (r.get("outcome") or "")[:160]
            lines.append(f"       target: {r.get('target','')} | success={r['success']}")
            lines.append(f"       outcome: {outcome}")
            if r.get("summary_en"):
                lines.append(f"       summary_en: {r['summary_en'][:100]}")
            if r.get("error_type"):
                lines.append(f"       error: {r['error_type']}: {(r.get('error_reason') or '')[:100]}")
            lines.append("")
        else:
            lines.append(f"       {(r.get('outcome') or '')[:80]}")
    return "\n".join(lines)


# ─── 混合检索 ──────────────────────────────────
def _hybrid_search(query, filtered, top_k, weights=(0.6, 0.4)):
    """
    混合检索：
      - full_bm25: 对 _build_doc (含中英文全文) 检索 → score_full
      - en_bm25: 对 _build_en_doc (仅英文字段) 检索 → score_en
      - final_score = w_full * norm(score_full) + w_en * norm(score_en)
    """
    docs_full = [_build_doc(r) for r in filtered]
    docs_en = [_build_en_doc(r) for r in filtered]

    bm25_full = BM25(docs_full)
    bm25_en = BM25(docs_en)

    # 分别跑 top_k * 3 先拿够候选
    results_full = bm25_full.search(query, top_k=top_k * 3)
    results_en = bm25_en.search(query, top_k=top_k * 3)

    # 合并：每个 doc_id 记录两种分数
    full_scores = {}
    en_scores = {}
    for r in results_full:
        full_scores[r["idx"]] = r["score"]
    for r in results_en:
        en_scores[r["idx"]] = r["score"]

    all_indices = set(full_scores.keys()) | set(en_scores.keys())
    if not all_indices:
        return []

    # L2 归一化
    full_vals = [full_scores.get(i, 0) for i in all_indices]
    en_vals = [en_scores.get(i, 0) for i in all_indices]
    full_norm = math.sqrt(sum(v * v for v in full_vals)) or 1
    en_norm = math.sqrt(sum(v * v for v in en_vals)) or 1

    w_full, w_en = weights
    scored = []
    for i in all_indices:
        score = w_full * (full_scores.get(i, 0) / full_norm) + w_en * (en_scores.get(i, 0) / en_norm)
        scored.append((score, i))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [{"score": round(s, 4), "idx": i} for s, i in scored[:top_k] if s > 0]


# ─── CLI ───────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(description="检索 action memory 经验（v2 双语）")
    parser.add_argument("--query", required=True)
    parser.add_argument("--method", choices=["bm25", "summary_bm25", "hybrid", "tfidf"],
                        default="bm25",
                        help="bm25=全文检索(含英文字段), summary_bm25=仅英文字段, hybrid=混合加权, tfidf=传统TF-IDF")
    parser.add_argument("--action-type", default=None, help="按 action_type 精确过滤")
    parser.add_argument("--only-success", action="store_true")
    parser.add_argument("--only-failure", action="store_true")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--show-report", "-r", action="store_true",
                        help="显示详细检索报告（含分数/记录元信息/英文摘要）")
    parser.add_argument("--log-retrieve", action="store_true",
                        help="将此次检索日志追加到 retrieve_log.jsonl")
    parser.add_argument("--no-header", action="store_true",
                        help="不输出 header（便于脚本调用解析）")
    parser.add_argument("--json-output", action="store_true",
                        help="以 JSON 格式输出结果（便于程序消费）")

    args = parser.parse_args()

    records = load_records()
    if not records:
        print("[·] action_memory.jsonl 为空或无数据", file=sys.stderr)
        print("[]" if args.json_output else "")
        return

    # 过滤
    filtered = records
    if args.action_type:
        filtered = [r for r in filtered if r.get("action_type") == args.action_type]
    if args.only_success:
        filtered = [r for r in filtered if r.get("success") is True]
    if args.only_failure:
        filtered = [r for r in filtered if r.get("success") is False]

    if not filtered:
        if not args.no_header:
            print("[·] 无匹配的记录可检索", file=sys.stderr)
        print("[]" if args.json_output else "")
        return

    # ── 检索 ──
    method = args.method
    if method == "summary_bm25":
        docs = [_build_en_doc(r) for r in filtered]
        engine = BM25(docs)
        results = engine.search(args.query, top_k=args.top_k)
    elif method == "hybrid":
        results = _hybrid_search(args.query, filtered, top_k=args.top_k)
    elif method == "bm25":
        docs = [_build_doc(r) for r in filtered]
        engine = BM25(docs)
        results = engine.search(args.query, top_k=args.top_k)
    else:
        docs = [_build_doc(r) for r in filtered]
        engine = TFIDF(docs)
        results = engine.search(args.query, top_k=args.top_k)

    # 重建结果
    formatted_results = []
    for res in results:
        rec = filtered[res["idx"]]
        formatted_results.append({
            "score": round(res["score"], 4),
            "case_id": rec.get("case_id"),
            "step": rec.get("step"),
            "action_type": rec.get("action_type"),
            "target": rec.get("target"),
            "success": rec.get("success"),
            "outcome": rec.get("outcome"),
            "summary_en": rec.get("summary_en"),
            "keywords": rec.get("keywords"),
            "error_type": rec.get("error_type"),
            "error_reason": rec.get("error_reason"),
        })

    # ── 输出 ──
    if args.json_output:
        print(json.dumps(formatted_results, ensure_ascii=False, indent=2))
        return

    if not args.no_header:
        method_name = {
            "bm25": "BM25(全文)", "summary_bm25": "BM25(英文摘要)",
            "hybrid": "混合(BM25全文+英文摘要)", "tfidf": "TF-IDF(全文)"
        }[method]
        filter_desc = []
        if args.action_type:
            filter_desc.append(f"action_type={args.action_type}")
        if args.only_success:
            filter_desc.append("仅成功")
        if args.only_failure:
            filter_desc.append("仅失败")
        filt = f" | {', '.join(filter_desc)}" if filter_desc else ""
        print(f"── {method_name} 检索报告 ──")
        print(f"  查询: \"{args.query}\"")
        print(f"  命中: {len(formatted_results)}/{len(filtered)} 条{filt}")
        print(f"  检索范围: {len(records)} 条总记录 → {len(filtered)} 条过滤后")
        print()

    print(_format_outcomes(formatted_results, show_detail=args.show_report))

    if not args.no_header:
        print(f"── 检索报告结束 ──")

    if args.log_retrieve:
        _log_retrieve(
            query=args.query,
            method=method,
            top_k=args.top_k,
            action_type_filter=args.action_type,
            only_success=args.only_success,
            only_failure=args.only_failure,
            results=formatted_results,
            config_snapshot={
                "enable": _config.get("enable"),
                "cold_start": _config.get("cold_start"),
                "require_retrieve_before": _config.get("require_retrieve_before"),
            },
        )
        if not args.no_header:
            print("[✓] 检索日志已记录")


if __name__ == "__main__":
    main()
