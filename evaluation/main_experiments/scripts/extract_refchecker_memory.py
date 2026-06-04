#!/usr/bin/env python3
"""Extract REFCHECKER_REPAIR_LOG rows and append normalized memory records."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_ITEM_TYPES = {"reference_metadata", "claim_citation_pair"}
ALLOWED_ISSUE_TYPES = {
    "none",
    "metadata_error",
    "support_error",
    "overclaim",
    "scope_error",
    "uncertain",
}
ALLOWED_REPAIR_ACTIONS = {
    "none",
    "correct_metadata",
    "remove_claim",
    "weaken_claim",
    "replace_citation",
    "mark_uncertain",
}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9._-]*", re.IGNORECASE)


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_log_block(text: str) -> str:
    start_match = re.search(r"^# REFCHECKER_REPAIR_LOG\s*$", text, flags=re.MULTILINE)
    if not start_match:
        raise ValueError("missing # REFCHECKER_REPAIR_LOG marker")
    end_match = re.search(r"^# REPAIRED_REPORT\s*$", text[start_match.end() :], flags=re.MULTILINE)
    if not end_match:
        raise ValueError("missing # REPAIRED_REPORT marker after repair log")
    return text[start_match.end() : start_match.end() + end_match.start()]


def parse_jsonl_from_block(block: str) -> list[dict[str, Any]]:
    lines: list[str] = []
    in_fence = False
    saw_fence = False
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("```"):
            saw_fence = True
            in_fence = not in_fence
            continue
        if saw_fence and not in_fence:
            continue
        if line.startswith("{"):
            lines.append(line)

    rows: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL line {idx}: {exc}: {line[:160]}") from exc
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def compact_summary(row: dict[str, Any]) -> str:
    issue = str(row.get("issue_summary", "")).strip()
    action = str(row.get("repair_action", "")).strip()
    item = str(row.get("item_id", "")).strip()
    tag = str(row.get("citation_tag", "")).strip()
    text = f"{item} [{tag}] {issue}"
    if action and action != "none":
        text += f" Repair action: {action}."
    text = re.sub(r"\s+", " ", text)
    if len(text) > 320:
        text = text[:317].rstrip() + "..."
    return text


def keywords_for(row: dict[str, Any], topic: str, case_id: str) -> list[str]:
    parts = [
        topic,
        case_id,
        str(row.get("item_type", "")),
        str(row.get("citation_tag", "")),
        str(row.get("issue_type", "")),
        str(row.get("repair_action", "")),
        str(row.get("item_id", "")),
    ]
    tokens = [tok.lower() for tok in TOKEN_RE.findall(" ".join(parts))]
    ordered: list[str] = []
    for token in tokens:
        if token not in ordered:
            ordered.append(token)
    return ordered[:48]


def load_existing_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    if not path.exists():
        return ids
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        record_id = obj.get("memory_record_id")
        if isinstance(record_id, str):
            ids.add(record_id)
    return ids


def normalize_row(row: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    case_id = str(row.get("case_id") or manifest["case_id"])
    source_run_id = str(row.get("run_id") or manifest["run_id"])
    pass_id = str(manifest.get("pass_id") or "")
    condition = str(manifest["condition"])
    item_id = str(row.get("item_id") or "unknown")

    item_type = str(row.get("item_type") or "claim_citation_pair")
    if item_type not in ALLOWED_ITEM_TYPES:
        item_type = "claim_citation_pair"

    issue_type = str(row.get("issue_type") or "uncertain").lower()
    if issue_type not in ALLOWED_ISSUE_TYPES:
        issue_type = "uncertain"

    repair_action = str(row.get("repair_action") or "mark_uncertain").lower()
    if repair_action not in ALLOWED_REPAIR_ACTIONS:
        repair_action = "mark_uncertain"

    normalized = {
        "memory_record_id": f"{condition}:{source_run_id}:{item_id}",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "condition": condition,
        "pass_id": pass_id,
        "case_id": case_id,
        "source_run_id": source_run_id,
        "topic": str(manifest.get("topic", "")),
        "item_id": item_id,
        "item_type": item_type,
        "citation_tag": str(row.get("citation_tag") or ""),
        "tool_called_refchecker": str(row.get("tool_called_refchecker") or "uncertain"),
        "refchecker_verified": str(row.get("refchecker_verified") or "uncertain"),
        "issue_type": issue_type,
        "issue_summary": str(row.get("issue_summary") or ""),
        "repair_action": repair_action,
    }
    normalized["summary_en"] = compact_summary(normalized)
    normalized["keywords"] = keywords_for(normalized, normalized["topic"], case_id)
    return normalized


def append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--manifest-file", required=True)
    parser.add_argument("--memory-file", required=True)
    parser.add_argument("--report-file")
    args = parser.parse_args()

    output_file = Path(args.output_file)
    manifest_file = Path(args.manifest_file)
    memory_file = Path(args.memory_file)
    manifest = load_manifest(manifest_file)

    text = output_file.read_text(encoding="utf-8", errors="replace")
    block = extract_log_block(text)
    rows = parse_jsonl_from_block(block)
    if not rows:
        raise SystemExit(f"No JSONL rows found in REFCHECKER_REPAIR_LOG: {output_file}")

    existing_ids = load_existing_ids(memory_file)
    records = [normalize_row(row, manifest) for row in rows]
    new_records = [record for record in records if record["memory_record_id"] not in existing_ids]
    append_jsonl(memory_file, new_records)

    report = {
        "output_file": str(output_file),
        "manifest_file": str(manifest_file),
        "memory_file": str(memory_file),
        "parsed_rows": len(rows),
        "new_records": len(new_records),
        "skipped_duplicates": len(records) - len(new_records),
    }
    if args.report_file:
        Path(args.report_file).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

