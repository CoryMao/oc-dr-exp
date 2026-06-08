#!/usr/bin/env python3
"""
写入一条 meta action 记录到 action_memory.jsonl。
v2 — 自动生成英文摘要（summary_en）和关键词列表（keywords）用于检索。

用法:
  # 从命令行参数
  python3 append.py \\
    --case-id exp_001 --step 1 \\
    --action-type fetch_paper --target "[D] arxiv:xxx" \\
    --success true \\
    --outcome "中文结果描述" \\
    --summary-en "English summary for retrieval" \\
    --keywords "key1, key2, key3" \\
    --is-claim-generation false

  # 从 JSON 文件
  python3 append.py --json path/to/record.json
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

# 读取配置文件
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "action_memory_config.json")
_default_memory = os.path.join(os.path.dirname(__file__), "action_memory.jsonl")


def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"enable": True, "memory_file": _default_memory}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        print(f"[!] 配置文件格式错误: {CONFIG_FILE}", file=sys.stderr)
        return {"enable": False}


_config = _load_config()
MEMORY_FILE = _config.get("memory_file", _default_memory)
if not os.path.isabs(MEMORY_FILE):
    MEMORY_FILE = os.path.join(os.path.dirname(__file__), MEMORY_FILE)

TZ = timezone(timedelta(hours=8))


def ensure_file():
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE) or ".", exist_ok=True)
        with open(MEMORY_FILE, "w") as f:
            f.write("")


def extract_keywords_from_outcome(outcome: str) -> list:
    """从中文 outcome 中提取有信息量的英文词做关键词"""
    if not outcome:
        return []
    # 提取 outcome 中的英文单词（至少2字符、首字母非数字）
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9._/-]+", outcome)
    # 过滤掉很短的词
    tokens = [t for t in tokens if len(t) >= 3]
    # 去重，保持顺序
    seen = set()
    result = []
    for t in tokens:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            result.append(t)
    return result[:20]


def generate_summary_en(outcome: str) -> str:
    """从 outcome 中提取英文摘要（纯拼接英文 token 的紧凑摘要）"""
    if not outcome:
        return ""
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9._/-]+", outcome)
    # 过滤短词和一些噪音
    tokens = [t for t in tokens if len(t) >= 3 and t not in ("the", "and", "for", "are", "was", "but", "not")]
    # 去重
    seen = set()
    result = []
    for t in tokens:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            result.append(t)
    return " ".join(result)


_REPORT_SCRIPT = os.path.join(os.path.dirname(__file__), "generate_recall_report.py")


def append_record(rec):
    if not _config.get("enable", True):
        print("[·] action memory 已关闭，跳过写入")
        return
    ensure_file()
    if "timestamp" not in rec or not rec.get("timestamp"):
        rec["timestamp"] = datetime.now(TZ).isoformat(timespec="seconds")

    # ── 自动补充 summary_en 和 keywords ─────────────────
    if "summary_en" not in rec or not rec.get("summary_en"):
        rec["summary_en"] = generate_summary_en(rec.get("outcome", ""))
    if "keywords" not in rec or not rec.get("keywords"):
        rec["keywords"] = extract_keywords_from_outcome(rec.get("outcome", ""))

    case_complete = rec.pop("_case_complete", False)

    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[✓] 已写入 step {rec.get('step')}: {rec.get('action_type')}")

    # ── 自动触发 recall report ───────────────────────────
    if case_complete:
        import subprocess
        case_id = rec.get("case_id", "unknown")
        # 默认输出到 scripts/ 下，如果有 _output_dir 则输出到指定目录
        output_dir = rec.pop("_output_dir", None) or os.path.dirname(__file__)
        out_path = os.path.join(output_dir, f"recall_audit_{case_id}.md")
        print(f"[📋] Case 完成，自动生成 recall audit: {out_path}")
        try:
            subprocess.run(
                [sys.executable, _REPORT_SCRIPT,
                 "--case-id", case_id,
                 "--output", out_path],
                capture_output=True, text=True, timeout=30
            )
            # 同时也复制一份到 memory_record 目录（如果 output_dir 不是 memory_record）
            print(f"[✓] Recall audit 已输出: {out_path}")
        except Exception as e:
            print(f"[!] Recall audit 生成失败: {e}", file=sys.stderr)


def cli():
    import argparse

    parser = argparse.ArgumentParser(description="追加 action memory 记录（v2 双语）")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--step", type=int, default=None)
    parser.add_argument("--action-type", default=None)
    parser.add_argument("--target", default="")
    parser.add_argument("--success", type=lambda x: x.lower() == "true", default=None)
    parser.add_argument("--outcome", default="")
    parser.add_argument("--summary-en", default=None, help="英文摘要（不传则自动从 outcome 提取英文 token）")
    parser.add_argument("--keywords", default=None, help="英文关键词列表（逗号分隔，不传则自动提取）")
    parser.add_argument("--is-claim-generation", type=lambda x: x.lower() == "true", default=False)
    parser.add_argument("--citation-error", type=lambda x: x.lower() == "true" if x else None, default=None)
    parser.add_argument("--error-type", default=None)
    parser.add_argument("--error-reason", default="")
    parser.add_argument("--case-complete", action="store_true",
                        help="标记 case 完成，自动生成 recall audit 报告")
    parser.add_argument("--context", default="")
    parser.add_argument("--json", default=None)
    parser.add_argument("--retrieve-before", action="store_true",
                        help="make_claim 前自动检索（高频检索的关键参数）")
    parser.add_argument("--retrieve-query", default=None,
                        help="检索查询词，不传则用 outcome 或 summary_en")
    parser.add_argument("--retrieve-method", default="summary_bm25",
                        help="检索方法: bm25/summary_bm25/hybrid/tfidf")
    parser.add_argument("--retrieve-top-k", type=int, default=5,
                        help="检索返回条数")
    parser.add_argument("--retrieve-filter", default=None,
                        help="检索过滤条件，如 'case_id=case_001' 或 'action_type=make_claim'")

    args = parser.parse_args()

    if args.json:
        with open(args.json, "r") as f:
            rec = json.load(f)
    else:
        # 手动验证必需参数
        missing = []
        if not args.case_id:
            missing.append("--case-id")
        if args.step is None:
            missing.append("--step")
        if not args.action_type:
            missing.append("--action-type")
        if args.success is None:
            missing.append("--success")
        if missing:
            parser.error(f"the following arguments are required: {', '.join(missing)}")

        rec = {
            "case_id": args.case_id,
            "step": args.step,
            "action_type": args.action_type,
            "target": args.target or None,
            "success": args.success,
            "outcome": args.outcome or None,
            "summary_en": args.summary_en or None,
            "keywords": [k.strip() for k in args.keywords.split(",")] if args.keywords else None,
            "is_claim_generation": args.is_claim_generation,
            "citation_error": args.citation_error,
            "error_type": args.error_type,
            "error_reason": args.error_reason or None,
            "context": args.context or None,
        }
    if args.case_complete:
        rec["_case_complete"] = True

    # ── auto-retrieve：make_claim 前自动检索 ────────────
    if args.retrieve_before and rec.get("action_type") in ("make_claim", "claim_generation", "fetch_paper", "search_paper"):
        import subprocess
        _retrieve_script = os.path.join(os.path.dirname(__file__), "retrieve.py")
        _query = args.retrieve_query or rec.get("summary_en", "") or rec.get("outcome", "") or ""
        _method = args.retrieve_method or "summary_bm25"
        _top_k = args.retrieve_top_k or 5
        print(f"[🔍] Auto-retrieve before {rec.get('action_type')}: '{_query[:60]}'")
        cmd = [sys.executable, _retrieve_script,
               "--query", _query,
               "--method", _method,
               "--top-k", str(_top_k)]
        if args.retrieve_filter:
            filters = [f.strip() for f in args.retrieve_filter.split(",")]
            for f in filters:
                if "=" in f:
                    k, v = f.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k == "action_type":
                        cmd += ["--action-type", v]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"[!] {result.stderr}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Auto-retrieve 失败: {e}", file=sys.stderr)

    append_record(rec)


if __name__ == "__main__":
    cli()
