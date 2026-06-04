#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="${MAIN_MEMORY_RUN_ROOT:-$ROOT_DIR/runs/main_memory}"
OUT_CSV="${OUT_CSV:-$ROOT_DIR/evaluation/main_experiments/main_memory_outputs.csv}"
TARGET_CONDITION="${MAIN_MEMORY_CONDITION:-memory_on}"

[[ -d "$RUN_ROOT" ]] || { echo "Run root does not exist: $RUN_ROOT" >&2; exit 1; }

python3 - "$RUN_ROOT" "$OUT_CSV" "$TARGET_CONDITION" <<'PY'
import csv
import json
import re
import sys
from pathlib import Path

run_root = Path(sys.argv[1])
out_csv = Path(sys.argv[2])
target_condition = sys.argv[3]

def marker_ok(run_dir: Path) -> str:
    raw = run_dir / "output.raw.txt"
    log = run_dir / "run.log"
    stderr = run_dir / "stderr.log"
    if not raw.exists() or not log.exists():
        return "no"
    text = raw.read_text(encoding="utf-8", errors="replace")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    stderr_text = stderr.read_text(encoding="utf-8", errors="replace") if stderr.exists() else ""
    markers = [
        "# ORIGINAL_REPORT",
        "# REFCHECKER_REPAIR_LOG",
        "# REPAIRED_REPORT",
        "# RUN_SUMMARY",
    ]
    if not all(re.search(rf"^{re.escape(marker)}", text, flags=re.MULTILINE) for marker in markers):
        return "no"
    if "markers_ok=yes" not in log_text:
        return "no"
    if re.search(r"Request timed out|Request was aborted|FailoverError|No API key found|MCP error -32000|MCP error -32001", text + "\n" + stderr_text):
        return "no"
    return "yes"

def count_nonempty(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())

rows = []
for manifest_path in sorted(run_root.rglob("run_manifest.json")):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if target_condition != "all" and data["condition"] != target_condition:
        continue
    run_dir = manifest_path.parent
    rows.append(
        {
            "condition": data["condition"],
            "case_id": data["case_id"],
            "run_id": data["run_id"],
            "pass_id": data.get("pass_id", ""),
            "openclaw_profile": data["openclaw_profile"],
            "markers_ok": marker_ok(run_dir),
            "memory_records_before": count_nonempty(run_dir / "memory_before.jsonl"),
            "memory_records_after": count_nonempty(run_dir / "memory_after.jsonl"),
            "prompt_file": data["prompt_file"],
            "raw_output_path": str(run_dir / "output.raw.txt"),
            "run_log_path": str(run_dir / "run.log"),
            "stderr_path": str(run_dir / "stderr.log"),
            "memory_context_path": str(run_dir / "memory_context.md") if data["condition"] == "memory_on" else "",
            "manifest_path": str(manifest_path),
        }
    )

out_csv.parent.mkdir(parents=True, exist_ok=True)
with out_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} rows to {out_csv}")
PY
