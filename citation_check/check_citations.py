# -*- coding: utf-8 -*-
"""逐条核验 LLM agent 报告的引用忠实度，汇总到一个 JSON。

用法（在 D:\\LLM\\agent_research 下）：
  # 凭证从环境变量读取：DEEPSEEK_API_KEY（或 --api-key），base_url/模型见默认值
  export DEEPSEEK_API_KEY=sk-xxxx
  python citation_check/check_citations.py
  python citation_check/check_citations.py --output-dir output --model deepseek-v4-pro
  python citation_check/check_citations.py --case 1 --run 1   # 只跑某个文件，便于调试

输出：citation_check/results.json
  只收录 error_type ∈ {Unsupported Claim, Overclaim, Mis-citation, Contradiction, Unverifiable} 的条目。
  Correct 的 claim 不写入。
每条字段：case_id, run_id, claim, error_type, repair_or_not
（脚本同时打印每个文件的全量统计，含 Correct 计数，方便算 precision/recall。）
"""
import os
import re
import sys
import json
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import parse_report as P
import pdf_extract as X
from prompts import SYSTEM_PROMPT, FEWSHOT, build_user_prompt

ERROR_TYPES = {"Unsupported Claim", "Overclaim", "Mis-citation", "Contradiction"}
RECORDED = ERROR_TYPES | {"Unverifiable"}


# ---- 模型调用 ---------------------------------------------------------

DEFAULT_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def make_client(api_key=None, base_url=None):
    from openai import OpenAI
    key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit(
            "缺少 API key。请设置环境变量 DEEPSEEK_API_KEY，或用 --api-key 传入。"
        )
    return OpenAI(api_key=key, base_url=base_url or DEFAULT_BASE_URL)


def call_model(client, model, user_prompt, max_retries=4):
    """调用模型并解析其 JSON 输出，返回 dict。失败抛异常。"""
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=1024,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + FEWSHOT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = (resp.choices[0].message.content or "").strip()
            return parse_model_json(text)
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise last_err


def parse_model_json(text):
    """从模型输出里抠出 JSON 对象。"""
    # 去掉可能的 ```json ... ``` 包裹
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    else:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            text = m.group(0)
    obj = json.loads(text)
    et = str(obj.get("error_type", "")).strip()
    # 规范化 error_type 大小写/别名
    obj["error_type"] = normalize_error_type(et)
    return obj


def normalize_error_type(et):
    low = et.lower().replace("_", " ").replace("-", " ").strip()
    table = {
        "unsupported claim": "Unsupported Claim",
        "unsupported": "Unsupported Claim",
        "overclaim": "Overclaim",
        "over claim": "Overclaim",
        "mis citation": "Mis-citation",
        "miscitation": "Mis-citation",
        "contradiction": "Contradiction",
        "correct": "Correct",
        "unverifiable": "Unverifiable",
    }
    return table.get(low, et if et else "Correct")


# ---- 文件发现 ---------------------------------------------------------

_RUNFILE = re.compile(r"^run(\d+)\.txt$", re.I)


def discover_files(output_dir, only_case=None, only_run=None):
    """返回 [(case_id, run_id, txt_path, paper_dir), ...]。case_id/run_id 为字符串数字。"""
    found = []
    for entry in sorted(os.listdir(output_dir)):
        cm = re.match(r"^case(\d+)$", entry, re.I)
        if not cm:
            continue
        case_id = cm.group(1)
        if only_case and case_id != str(only_case):
            continue
        case_dir = os.path.join(output_dir, entry)
        if not os.path.isdir(case_dir):
            continue
        paper_dir = os.path.join(case_dir, "paper")
        for f in sorted(os.listdir(case_dir)):
            rm = _RUNFILE.match(f)
            if not rm:
                continue
            run_id = rm.group(1)
            if only_run and run_id != str(only_run):
                continue
            found.append((case_id, run_id, os.path.join(case_dir, f), paper_dir))
    return found


# ---- 单条 claim 核验 --------------------------------------------------

def verify_one_claim(client, model, claim_text, citation_str, refs,
                     paper_dir, cache_dir, paper_text_cache):
    """核验一条 claim。返回 (error_type, detail_dict)。

    若引用的任一论文 PDF 缺失 -> 直接判 Unverifiable，不调用模型。
    """
    tags = P.tags_in_citation(citation_str)
    if not tags:
        # 没有任何出处标签：按方案，无引用支撑的实质结论属 Unsupported Claim
        return "Unsupported Claim", {"reason": "claim 未标注任何 [A]~[F] 出处"}

    papers, missing = [], []
    for tag in tags:
        ref = refs.get(tag, {})
        title = ref.get("title") or tag
        key = (paper_dir, tag)
        if key not in paper_text_cache:
            pdf, text = X.get_paper_text(title, paper_dir, cache_dir)
            paper_text_cache[key] = (pdf, text)
        pdf, text = paper_text_cache[key]
        if not text:
            missing.append(tag)
        papers.append({
            "tag": tag, "title": title,
            "ref_line": ref.get("ref_line", ""), "text": text,
        })

    if missing:
        return "Unverifiable", {
            "reason": "引用论文 PDF 缺失或无法抽取: " + ",".join(missing),
            "missing_tags": missing,
        }

    user_prompt = build_user_prompt(claim_text, citation_str, papers)
    obj = call_model(client, model, user_prompt)
    return obj.get("error_type", "Correct"), obj


# ---- 主流程 -----------------------------------------------------------

def _fmt_eta(seconds):
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def count_claims(files):
    """预扫描所有文件，统计待核验 claim 总数（两版相加），用于进度分母。"""
    total = 0
    for _, _, txt_path, _ in files:
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception:
            continue
        for _, vt in P.split_versions(raw):
            total += len(P.parse_claims(vt))
    return total


def process_file(client, model, case_id, run_id, txt_path, paper_dir,
                 cache_dir, prog, all_records, result_path):
    """处理一个 run 文件的两版报告，返回该文件的 stats。

    prog: 共享进度字典 {done, total, t0}；每核验一条就刷新进度并增量写盘。
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    stats = {}  # repair_or_not -> {error_type: count}
    for repair_flag, version_text in P.split_versions(raw):
        refs = P.parse_references(version_text)
        claims = P.parse_claims(version_text)
        paper_text_cache = {}
        vstats = {}
        for idx, (claim_text, citation_str) in enumerate(claims, 1):
            error_type, detail = verify_one_claim(
                client, model, claim_text, citation_str,
                refs, paper_dir, cache_dir, paper_text_cache,
            )
            vstats[error_type] = vstats.get(error_type, 0) + 1

            prog["done"] += 1
            done, total = prog["done"], prog["total"]
            elapsed = time.time() - prog["t0"]
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            pct = 100.0 * done / total if total else 0
            bar_n = int(pct // 5)
            bar = "#" * bar_n + "-" * (20 - bar_n)
            flag = "no " if repair_flag == "no" else "yes"
            mark = "  " if error_type == "Correct" else "!!"
            # 进度行（覆盖式）
            print(
                f"[{bar}] {done}/{total} {pct:4.1f}% 用时{_fmt_eta(elapsed)} "
                f"剩~{_fmt_eta(eta)} | c{case_id}r{run_id}/{flag} #{idx:02d} "
                f"{mark}{error_type}",
                flush=True,
            )

            if error_type in RECORDED:
                all_records.append({
                    "case_id": case_id,
                    "run_id": run_id,
                    "claim": claim_text,
                    "error_type": error_type,
                    "repair_or_not": repair_flag,
                })
                # 增量写盘：任何时刻中断都不丢已得结果
                _save(all_records, result_path)
        stats[repair_flag] = vstats
    return stats


def _save(records, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="output")
    ap.add_argument("--model", default=os.environ.get("CHECK_MODEL", "deepseek-v4-pro"))
    ap.add_argument("--api-key", default=None, help="覆盖环境变量 DEEPSEEK_API_KEY")
    ap.add_argument("--base-url", default=None, help="覆盖默认 base_url")
    ap.add_argument("--result", default=os.path.join("citation_check", "results.json"))
    ap.add_argument("--cache-dir", default=os.path.join("citation_check", ".cache"))
    ap.add_argument("--case", default=None, help="只跑某个 case 编号")
    ap.add_argument("--run", default=None, help="只跑某个 run 编号")
    args = ap.parse_args()

    files = discover_files(args.output_dir, args.case, args.run)
    if not files:
        print("没有发现 output/caseN/runM.txt 文件。检查 --output-dir。")
        return

    total = count_claims(files)
    print(f"发现 {len(files)} 个 run 文件，共 {total} 条 claim 待核验，模型: {args.model}")
    print("（每条 = 一次模型调用；缺 PDF 的直接判 Unverifiable，不调用模型）\n")

    client = make_client(args.api_key, args.base_url)
    all_records = []
    all_stats = []
    prog = {"done": 0, "total": total, "t0": time.time()}
    for case_id, run_id, txt_path, paper_dir in files:
        print(f"\n== case{case_id} run{run_id} ==")
        stats = process_file(
            client, args.model, case_id, run_id, txt_path, paper_dir,
            args.cache_dir, prog, all_records, args.result,
        )
        all_stats.append((case_id, run_id, stats))

    _save(all_records, args.result)

    print("\n================ 汇总 ================")
    print(f"总用时 {_fmt_eta(time.time() - prog['t0'])}")
    print(f"写入 {len(all_records)} 条问题记录 -> {args.result}")
    et_total = {}
    for r in all_records:
        et_total[r["error_type"]] = et_total.get(r["error_type"], 0) + 1
    for et, n in sorted(et_total.items()):
        print(f"  {et}: {n}")
    print("\n各文件全量分布（含 Correct，用于算 precision/recall）:")
    for case_id, run_id, stats in all_stats:
        for flag, vs in stats.items():
            dist = ", ".join(f"{k}={v}" for k, v in sorted(vs.items()))
            print(f"  case{case_id} run{run_id} repair={flag}: {dist}")


if __name__ == "__main__":
    main()
