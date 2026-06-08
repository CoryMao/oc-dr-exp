#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="${MAIN_MEMORY_RUN_ROOT:-$ROOT_DIR/runs/main_memory}"
CASE_PAPER_DIR="$ROOT_DIR/case paper"
TARGET_CONDITION="${MAIN_MEMORY_CONDITION:-memory_on}"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -d "$RUN_ROOT" ]] || fail "Run root does not exist: $RUN_ROOT"
[[ -d "$CASE_PAPER_DIR" ]] || fail "Case paper directory does not exist: $CASE_PAPER_DIR"

m1_count="$(find "$RUN_ROOT/M1_memory_on" -name prompt.base.md 2>/dev/null | wc -l | tr -d ' ')"
m0_count="$(find "$RUN_ROOT/M0_no_memory" -name prompt.md 2>/dev/null | wc -l | tr -d ' ')"

if [[ "$TARGET_CONDITION" == "memory_on" ]]; then
  [[ "$m1_count" == "10" ]] || fail "Expected 10 M1 prompt bases, found $m1_count"
elif [[ "$TARGET_CONDITION" == "all" ]]; then
  [[ "$m0_count" == "15" ]] || fail "Expected 15 M0 prompts, found $m0_count"
  [[ "$m1_count" == "10" ]] || fail "Expected 10 M1 prompt bases, found $m1_count"
else
  fail "Unsupported MAIN_MEMORY_CONDITION=$TARGET_CONDITION. Use memory_on or all."
fi

for case_num in 1 2 3 4 5; do
  pdf_count="$(find "$CASE_PAPER_DIR/case${case_num}" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
  [[ "$pdf_count" -ge 2 ]] || fail "Expected PDFs for case${case_num}, found $pdf_count"
done

python3 - "$RUN_ROOT" "$TARGET_CONDITION" <<'PY'
import json
import sys
from pathlib import Path

run_root = Path(sys.argv[1])
target_condition = sys.argv[2]
errors = []
seen_m1 = []

for manifest_path in sorted(run_root.rglob("run_manifest.json")):
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    condition = data["condition"]
    if target_condition == "memory_on" and condition != "memory_on":
        continue
    prompt_file = Path(data["prompt_file"])
    prompt_base = Path(data["prompt_base_file"])
    if condition == "no_memory":
        if not prompt_file.exists():
            errors.append(f"missing no-memory prompt: {prompt_file}")
        if "{run_id}" in prompt_file.read_text(encoding="utf-8"):
            errors.append(f"unexpanded run_id placeholder: {prompt_file}")
        if data["memory"]["enabled"]:
            errors.append(f"no-memory manifest has memory enabled: {manifest_path}")
    elif condition == "memory_on":
        seen_m1.append((data["pass_id"], data["case_id"], manifest_path))
        if not prompt_base.exists():
            errors.append(f"missing memory prompt base: {prompt_base}")
        if prompt_file.exists() and "{run_id}" in prompt_file.read_text(encoding="utf-8"):
            errors.append(f"unexpanded run_id placeholder: {prompt_file}")
        if "{run_id}" in prompt_base.read_text(encoding="utf-8"):
            errors.append(f"unexpanded run_id placeholder: {prompt_base}")
        if not data["memory"]["enabled"]:
            errors.append(f"memory manifest has memory disabled: {manifest_path}")
    else:
        errors.append(f"unknown condition in {manifest_path}: {condition}")

expected_m1 = [(f"P{p}", f"C{c}") for p in range(1, 3) for c in range(1, 6)]
actual_m1 = [(p, c) for p, c, _ in seen_m1]
if actual_m1 != expected_m1:
    errors.append(f"M1 order mismatch: {actual_m1}")

if errors:
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    raise SystemExit(1)
PY

echo "Preflight passed for main memory experiment."
