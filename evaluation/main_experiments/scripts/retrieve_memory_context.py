#!/usr/bin/env python3
"""Retrieve compact procedural memory for the main memory experiment."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._-]*", re.IGNORECASE)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def tokens_for(row: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for key in [
        "topic",
        "case_id",
        "item_type",
        "citation_tag",
        "issue_type",
        "issue_summary",
        "repair_action",
        "summary_en",
    ]:
        value = row.get(key)
        if isinstance(value, str):
            parts.append(value)
    keywords = row.get("keywords")
    if isinstance(keywords, list):
        parts.extend(str(item) for item in keywords)
    return [tok.lower() for tok in TOKEN_RE.findall(" ".join(parts))]


def score_rows(query: str, rows: list[dict[str, Any]]) -> list[tuple[float, dict[str, Any]]]:
    query_tokens = [tok.lower() for tok in TOKEN_RE.findall(query)]
    if not rows:
        return []
    if not query_tokens:
        query_tokens = ["citation", "support", "metadata", "repair"]

    docs = [Counter(tokens_for(row)) for row in rows]
    doc_freq: Counter[str] = Counter()
    for doc in docs:
        for token in doc:
            doc_freq[token] += 1

    n_docs = len(docs)
    query_counts = Counter(query_tokens)
    scored: list[tuple[float, dict[str, Any]]] = []
    for row, doc in zip(rows, docs):
        score = 0.0
        length_norm = 1.0 + math.log1p(sum(doc.values()))
        for token, q_count in query_counts.items():
            tf = doc.get(token, 0)
            if not tf:
                continue
            idf = math.log((1 + n_docs) / (1 + doc_freq[token])) + 1.0
            score += q_count * (1.0 + math.log(tf)) * idf / length_norm

        issue_type = str(row.get("issue_type", "")).lower()
        if issue_type and issue_type != "none":
            score += 1.5
        if str(row.get("repair_action", "")).lower() not in {"", "none"}:
            score += 0.5
        if str(row.get("case_id", "")).lower() in query.lower():
            score += 0.75

        scored.append((score, row))

    scored.sort(
        key=lambda item: (
            item[0],
            str(item[1].get("issue_type", "")).lower() != "none",
            str(item[1].get("created_at_utc", "")),
        ),
        reverse=True,
    )
    return scored


def render_context(selected: list[dict[str, Any]], *, top_k: int, max_chars: int) -> str:
    lines = [
        "## OUTPUT_CONTRACT_REMINDER",
        "",
        "Your final response must include exactly these four top-level headings in this order:",
        "# ORIGINAL_REPORT",
        "# REFCHECKER_REPAIR_LOG",
        "# REPAIRED_REPORT",
        "# RUN_SUMMARY",
        "Do not omit # ORIGINAL_REPORT. Do not output any prelude or explanation before the required report sections.",
        "",
        "## MEMORY_CONTEXT",
        "",
        "These prior records are procedural cautions only. Do not cite them. They are not scientific evidence.",
        "All scientific claims must still be supported by [A]-[F] source materials and CPS locations.",
        "",
    ]
    if not selected:
        lines.extend(
            [
                "No prior refchecker repair records were retrieved for this run.",
                "",
                "## TASK_PROMPT",
                "",
            ]
        )
        return "\n".join(lines)

    lines.append(f"Retrieved top {min(top_k, len(selected))} prior refchecker repair records:")
    for idx, row in enumerate(selected[:top_k], start=1):
        issue = str(row.get("issue_type", "unknown"))
        action = str(row.get("repair_action", "unknown"))
        source = str(row.get("source_run_id", row.get("run_id", "")))
        case_id = str(row.get("case_id", ""))
        item_id = str(row.get("item_id", ""))
        tag = str(row.get("citation_tag", ""))
        summary = str(row.get("summary_en") or row.get("issue_summary") or "").strip()
        summary = re.sub(r"\s+", " ", summary)
        if len(summary) > 220:
            summary = summary[:217].rstrip() + "..."
        lines.append(
            f"- M{idx}: source={source} case={case_id} item={item_id} tag={tag} issue={issue} action={action}; {summary}"
        )
    lines.extend(["", "Use these records only to avoid repeating citation metadata/support mistakes.", "", "## TASK_PROMPT", ""])

    rendered = "\n".join(lines)
    if len(rendered) <= max_chars:
        return rendered
    keep = rendered[: max_chars - 120].rstrip()
    return keep + "\n\n[MEMORY_CONTEXT truncated by max context character budget.]\n\n## TASK_PROMPT\n"


def append_retrieve_log(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-file", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--pass-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--max-context-chars", type=int, default=5000)
    parser.add_argument("--out", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    memory_file = Path(args.memory_file)
    out_path = Path(args.out)
    log_file = Path(args.log_file)

    rows = load_jsonl(memory_file)
    scored = score_rows(args.query, rows)
    selected = [row for score, row in scored[: args.top_k] if score > 0]
    context = render_context(selected, top_k=args.top_k, max_chars=args.max_context_chars)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(context, encoding="utf-8")

    append_retrieve_log(
        log_file,
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "case_id": args.case_id,
            "pass_id": args.pass_id,
            "run_id": args.run_id,
            "query": args.query,
            "memory_file": str(memory_file),
            "memory_record_count": len(rows),
            "top_k": args.top_k,
            "selected_record_ids": [str(row.get("memory_record_id", "")) for row in selected],
            "selected_count": len(selected),
            "context_file": str(out_path),
        },
    )
    print(f"retrieved={len(selected)} memory_records={len(rows)} out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
