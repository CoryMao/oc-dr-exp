#!/usr/bin/env python3
"""
Action Memory Recall Report Generator

在每个 Case 完成后，或者在全周期结束时，输出一份 memory recall 审计报告。
记录：
  - 每次检索触发的 time / query / action context
  - 命中了什么记录（score / case / step / outcome）
  - 命中是否来自当前 case（same-case?）还是跨 case
  - 是否 0 命中
  - 综合评估：检索是否为当前 action 提供了有意义的参考

用法:
  # 查看所有 case 的总体概览
  python3 generate_recall_report.py

  # 输出指定 case 的详细 recall audit
  python3 generate_recall_report.py --case-id case_004

  # 输出到文件（同时打印摘要）
  python3 generate_recall_report.py --case-id case_004 --output recall_audit_case4.md

  # 只看最近 N 次检索
  python3 generate_recall_report.py --recent 10

  # 只看 0 命中的检索（冷启动 / 首次探索）
  python3 generate_recall_report.py --show-zeros
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(__file__)
RETRIEVE_LOG = os.path.join(SCRIPT_DIR, "retrieve_log.jsonl")
MEMORY_FILE = os.path.join(SCRIPT_DIR, "action_memory.jsonl")


def load_retrieve_logs():
    if not os.path.exists(RETRIEVE_LOG):
        return []
    with open(RETRIEVE_LOG, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_memory_records():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_rec_lookup(records):
    lookup = {}
    for r in records:
        lookup[(r.get("case_id"), r.get("step"))] = r
    return lookup


def classify_hit_type(hit_case_id, current_case_id):
    """判断一个命中是 same-case, cross-case 还是 unknown"""
    if not hit_case_id:
        return "unknown"
    if hit_case_id == current_case_id:
        return "same-case"
    return f"cross-case({hit_case_id})"


def build_report(case_id=None, recent=None, show_zeros=False):
    logs = load_retrieve_logs()
    records = load_memory_records()
    rec_lookup = build_rec_lookup(records)

    if not logs:
        print("[·] retrieve_log.jsonl 为空，无检索记录")
        return

    # 按 case 去猜测每次检索对应的 case_id（从结果推断）
    retrievals = []
    for log in logs:
        ts = log["timestamp"]
        query = log["query"]
        method = log.get("method", "bm25")
        top_k = log.get("top_k", 3)
        num = log.get("num_results", 0)
        results_raw = log.get("results", [])

        # 猜测当前 case：大多数结果来自哪个 case
        case_votes = defaultdict(int)
        context_case_id = None
        for r in results_raw:
            cid = r.get("case_id")
            if cid:
                case_votes[cid] += 1
        if case_votes:
            context_case_id = max(case_votes, key=case_votes.get)

        hits = []
        for r in results_raw:
            hit_rec = rec_lookup.get((r.get("case_id"), r.get("step")))
            hit = {
                "score": r.get("score", 0),
                "case_id": r.get("case_id"),
                "step": r.get("step"),
                "action_type": r.get("action_type"),
                "success": r.get("success"),
                "outcome_short": (r.get("outcome") or "")[:100],
                "hit_type": classify_hit_type(r.get("case_id"), context_case_id),
            }
            if hit_rec:
                hit["outcome_short"] = (hit_rec.get("outcome") or "")[:100]
            hits.append(hit)

        retrievals.append({
            "timestamp": ts,
            "query": query,
            "method": method,
            "top_k": top_k,
            "num_results": num,
            "context_case_id": context_case_id,
            "hits": hits,
        })

    # ── 过滤 ──
    if case_id:
        retrievals = [r for r in retrievals if r["context_case_id"] == case_id]
    if recent:
        retrievals = retrievals[-recent:]
    if show_zeros:
        retrievals = [r for r in retrievals if r["num_results"] == 0]

    return retrievals


def print_report_summary(retrievals):
    """打印概要"""
    total = len(retrievals)
    if total == 0:
        print("  无匹配检索")
        return

    zero_hits = sum(1 for r in retrievals if r["num_results"] == 0)
    total_hits = sum(len(r["hits"]) for r in retrievals)

    # same-case vs cross-case
    same_hits = 0
    cross_hits = 0
    for r in retrievals:
        cid = r["context_case_id"]
        for h in r["hits"]:
            if h["hit_type"] == "same-case":
                same_hits += 1
            elif h["hit_type"].startswith("cross-case("):
                cross_hits += 1

    print(f"  检索次数: {total}")
    print(f"  总命中数: {total_hits}（平均 {total_hits/max(total,1):.1f}/次）")
    print(f"  零命中次数: {zero_hits}（{zero_hits/max(total,1)*100:.0f}%）")
    if total_hits > 0:
        print(f"  same-case 命中: {same_hits}（{same_hits/max(total_hits,1)*100:.0f}%）")
        print(f"  cross-case 命中: {cross_hits}（{cross_hits/max(total_hits,1)*100:.0f}%）")


def print_detailed_report(retrievals, case_id=None):
    """打印详细报告"""
    for i, r in enumerate(retrievals):
        ts = r["timestamp"]
        q = r["query"]
        cid = r["context_case_id"]
        print(f"─── #{i+1} {ts} ───")
        print(f"  Context: {cid}")
        print(f"  Query: {q[:80]}")
        print(f"  Method: {r['method']} | top_k: {r['top_k']} | hits: {r['num_results']}")

        if r["num_results"] == 0:
            print(f"  ⚪ 零命中 — 首次探索或 query 太偏")
        else:
            for h in r["hits"]:
                # same/cross 标志
                if h["hit_type"] == "same-case":
                    marker = "✓ SAME"
                elif h["hit_type"].startswith("cross-case("):
                    marker = f"↗ {h['hit_type'][12:-1]}"  # 提取 case_id
                else:
                    marker = "? ?"

                success_mark = "✓" if h["success"] else "✗"
                print(f"    [{h['score']:.2f}] {marker} {success_mark} "
                      f"{h['case_id']}:step{h['step']} [{h['action_type']}]")
                print(f"      \"{h['outcome_short'][:80]}\"")
        print()


def generate_markdown_report(retrievals, case_id=None):
    """生成 Markdown 报告"""
    lines = []
    lines.append(f"# Action Memory Recall Audit{' — ' + case_id if case_id else ''}")
    lines.append("")
    lines.append(f"> Generated: {datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    total = len(retrievals)
    zero_hits = sum(1 for r in retrievals if r["num_results"] == 0)
    total_hits = sum(len(r["hits"]) for r in retrievals)
    same_hits = sum(1 for r in retrievals for h in r["hits"] if h["hit_type"] == "same-case")
    cross_hits = sum(1 for r in retrievals for h in r["hits"] if h["hit_type"].startswith("cross-case("))
    lines.append(f"- **Total retrievals:** {total}")
    lines.append(f"- **Total hits:** {total_hits} (avg {total_hits/max(total,1):.1f}/retrieval)")
    lines.append(f"- **Zero-hit retrievals:** {zero_hits} ({zero_hits/max(total,1)*100:.0f}%)")
    if total_hits > 0:
        lines.append(f"- **Same-case hits:** {same_hits} ({same_hits/max(total_hits,1)*100:.0f}%)")
        lines.append(f"- **Cross-case hits:** {cross_hits} ({cross_hits/max(total_hits,1)*100:.0f}%)")
    lines.append("")

    lines.append("## Retrieval Log Detail")
    lines.append("")
    for i, r in enumerate(retrievals):
        ts = r["timestamp"]
        q = r["query"]
        method = r["method"]
        top_k = r["top_k"]
        hits_count = r["num_results"]
        cid = r["context_case_id"] or "unknown"
        lines.append(f"### #{i+1}: {ts}")
        lines.append("")
        lines.append(f"- **Context:** `{cid}`")
        lines.append(f"- **Query:** `{q}`")
        lines.append(f"- **Method:** `{method}` | top_k: `{top_k}`")
        lines.append(f"- **Hits:** {hits_count}")
        lines.append("")

        if hits_count == 0:
            lines.append("> ⚪ Zero-hit — first exploration or query mismatch")
            lines.append("")
        else:
            lines.append("| Score | Hit Relation | Success | Case:Step | Action Type | Outcome Excerpt |")
            lines.append("|-------|-------------|---------|-----------|-------------|-----------------|")
            for h in r["hits"]:
                hit_relation = h["hit_type"]
                icon = "✅" if h["success"] else "❌"
                loc = f"`{h['case_id']}:step{h['step']}`"
                act = f"`{h['action_type']}`"
                outcome = h["outcome_short"][:60].replace("|", "/")
                lines.append(f"| {h['score']:.2f} | {hit_relation} | {icon} | {loc} | {act} | {outcome} |")
            lines.append("")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Action Memory Recall Report Generator")
    parser.add_argument("--case-id", default=None, help="只显示指定 case 的检索记录")
    parser.add_argument("--recent", type=int, default=None, help="只显示最近 N 次检索")
    parser.add_argument("--show-zeros", action="store_true", help="只显示 0 命中的检索")
    parser.add_argument("--output", default=None, help="输出到 markdown 文件")

    args = parser.parse_args()

    retrievals = build_report(
        case_id=args.case_id,
        recent=args.recent,
        show_zeros=args.show_zeros,
    )

    if not retrievals:
        print(f"[·] 无匹配检索记录")
        sys.exit(0)

    if args.output:
        md = generate_markdown_report(retrievals, case_id=args.case_id)
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(md)
        print(f"[✓] Recall report 已输出: {args.output}")
        print()

    # 总是打印概要 + 详细报告
    print("=" * 50)
    print("📊 Recall Report Summary")
    print("=" * 50)
    print_report_summary(retrievals)
    print()
    print("=" * 50)
    print("📋 Recall Report Detail")
    print("=" * 50)
    print_detailed_report(retrievals, case_id=args.case_id)


if __name__ == "__main__":
    main()
