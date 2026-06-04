#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_refchecker_repair"
OUT_FILE="$ROOT_DIR/evaluation/pre_experiments/refchecker_repair_agent_outputs.csv"

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  exit 1
fi

printf 'case_id,run_id,condition,openclaw_profile,markers_ok,raw_output_path,run_log_path,stderr_path\n' > "$OUT_FILE"

while IFS= read -r manifest; do
  run_dir="$(dirname "$manifest")"
  condition="$(basename "$run_dir")"
  run_id="$(basename "$(dirname "$run_dir")")"
  case_id="$(basename "$(dirname "$(dirname "$run_dir")")")"
  profile="$(grep -E '"openclaw_profile":' "$manifest" | sed -E 's/.*"openclaw_profile": "([^"]+)".*/\1/')"
  markers_ok="missing"
  if [[ -f "$run_dir/run.log" ]]; then
    markers_ok="$(grep -E '^markers_ok=' "$run_dir/run.log" | tail -n 1 | sed -E 's/^markers_ok=//')"
    if [[ -z "$markers_ok" ]]; then
      markers_ok="missing"
    fi
  fi
  printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$case_id" \
    "$run_id" \
    "$condition" \
    "$profile" \
    "$markers_ok" \
    "$run_dir/output.raw.txt" \
    "$run_dir/run.log" \
    "$run_dir/stderr.log" >> "$OUT_FILE"
done < <(find "$RUN_ROOT" -name run_manifest.json | sort)

echo "Wrote: $OUT_FILE"
