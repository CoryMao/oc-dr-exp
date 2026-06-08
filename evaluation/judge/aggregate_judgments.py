#!/usr/bin/env python3
"""Aggregate LLM citation-judge JSONL into error-rate tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ERROR_TYPES = [
    "Unsupported Claim",
    "Overclaim",
    "Mis-citation",
    "Contradiction",
    "Correct",
    "NeedMoreContext",
    "Unverifiable",
]

FINAL_ERROR_TYPES = ["Unsupported Claim", "Overclaim", "Mis-citation", "Contradiction"]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def normalize_error_type(value: str) -> str:
    value = (value or "").strip()
    aliases = {
        "Unsupported": "Unsupported Claim",
        "unsupported": "Unsupported Claim",
        "overclaim": "Overclaim",
        "miscitation": "Mis-citation",
        "Mis Citation": "Mis-citation",
        "mis-citation": "Mis-citation",
        "contradiction": "Contradiction",
        "correct": "Correct",
        "needmorecontext": "NeedMoreContext",
        "Need More Context": "NeedMoreContext",
        "unverifiable": "Unverifiable",
    }
    return aliases.get(value, aliases.get(value.lower(), value if value in ERROR_TYPES else "NeedMoreContext"))


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", required=True, help="claim_citation_pairs.jsonl from build_judge_inputs.py")
    parser.add_argument("--judgments", required=True, help="LLM JSONL output; one row per item_id")
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--missing-as", choices=["NeedMoreContext", "Unverifiable"], default="NeedMoreContext")
    args = parser.parse_args()

    pairs = load_jsonl(Path(args.pairs))
    judgments = {row.get("item_id"): row for row in load_jsonl(Path(args.judgments))}

    by_group: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    details = []
    for pair in pairs:
        item_id = pair["item_id"]
        group = (pair["case_id"], pair["pass_id"], pair["report_version"])
        if pair.get("unverifiable"):
            error_type = "Unverifiable"
        elif item_id not in judgments:
            error_type = args.missing_as
        else:
            error_type = normalize_error_type(str(judgments[item_id].get("error_type", "")))
        by_group[group][error_type] += 1
        by_group[("ALL", "ALL", pair["report_version"])][error_type] += 1
        details.append({**pair, "judged_error_type": error_type})

    rows = []
    for (case_id, pass_id, report_version), counts in sorted(by_group.items()):
        total = sum(counts.values())
        unverifiable = counts["Unverifiable"]
        denominator = total - unverifiable
        final_error_count = sum(counts[name] for name in FINAL_ERROR_TYPES)
        row = {
            "case_id": case_id,
            "pass_id": pass_id,
            "report_version": report_version,
            "total_pairs": total,
            "verifiable_pairs": denominator,
            "unverifiable_pairs": unverifiable,
            "unsupported_count": counts["Unsupported Claim"],
            "overclaim_count": counts["Overclaim"],
            "miscitation_count": counts["Mis-citation"],
            "contradiction_count": counts["Contradiction"],
            "correct_count": counts["Correct"],
            "need_more_context_count": counts["NeedMoreContext"],
            "overall_error_rate": pct(final_error_count, denominator),
            "unsupported_rate": pct(counts["Unsupported Claim"], denominator),
            "overclaim_rate": pct(counts["Overclaim"], denominator),
            "miscitation_rate": pct(counts["Mis-citation"], denominator),
            "contradiction_rate": pct(counts["Contradiction"], denominator),
            "need_more_context_rate": pct(counts["NeedMoreContext"], denominator),
        }
        rows.append(row)

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
