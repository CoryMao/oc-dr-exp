#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_arxiv"
JOBS="${JOBS:-1}"
THINKING_LEVEL="${EXPERIMENT_THINKING:-high}"

if [[ -z "${OPENCLAW_RUN_CMD:-}" ]]; then
  cat >&2 <<'EOF'
OPENCLAW_RUN_CMD is not set.

Set it to a shell command that reads the prompt from $PROMPT_FILE and writes
the agent output to stdout. The runner exports:

  RUN_DIR
  PROMPT_FILE
  MANIFEST_FILE
  OUTPUT_FILE
  RAW_OUTPUT_FILE
  CONDITION
  CASE_ID
  RUN_ID
  OPENCLAW_PROFILE
  SESSION_KEY
  THINKING_LEVEL

Example shape:

  export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'

Then run:

  JOBS=1 bash evaluation/pre_experiments/scripts/run_arxiv_runs.sh
EOF
  exit 1
fi

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  echo "Run prepare_arxiv_runs.sh first." >&2
  exit 1
fi

run_one() {
  local prompt_file="$1"
  local run_dir manifest_file output_file raw_output_file run_log_file condition case_id run_id openclaw_profile session_key csv_rows
  run_dir="$(dirname "$prompt_file")"
  manifest_file="$run_dir/run_manifest.json"
  output_file="$run_dir/output.csv"
  raw_output_file="$run_dir/output.raw.txt"
  run_log_file="$run_dir/run.log"
  condition="$(basename "$run_dir")"
  run_id="$(basename "$(dirname "$run_dir")")"
  case_id="$(basename "$(dirname "$(dirname "$run_dir")")")"
  openclaw_profile="$(grep -E '"openclaw_profile":' "$manifest_file" | sed -E 's/.*"openclaw_profile": "([^"]+)".*/\1/')"
  session_key="arxiv-pre-${case_id}-${run_id}-${condition}"

  export RUN_DIR="$run_dir"
  export PROMPT_FILE="$prompt_file"
  export MANIFEST_FILE="$manifest_file"
  export OUTPUT_FILE="$output_file"
  export RAW_OUTPUT_FILE="$raw_output_file"
  export CONDITION="$condition"
  export CASE_ID="$case_id"
  export RUN_ID="$run_id"
  export OPENCLAW_PROFILE="$openclaw_profile"
  export SESSION_KEY="$session_key"
  export THINKING_LEVEL="$THINKING_LEVEL"

  {
    echo "=== START $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
    echo "case_id=$CASE_ID run_id=$RUN_ID condition=$CONDITION"
    echo "openclaw_profile=$OPENCLAW_PROFILE session_key=$SESSION_KEY"
    echo "thinking=$THINKING_LEVEL"
    bash -lc "$OPENCLAW_RUN_CMD" > "$raw_output_file"
    grep -E "^[Cc][0-9]+,R[123],arxiv_(on|off)," "$raw_output_file" > "$output_file" || true
    csv_rows="$(wc -l < "$output_file" | tr -d ' ')"
    echo "csv_rows=$csv_rows"
    if [[ "$csv_rows" != "3" ]]; then
      echo "WARNING: expected 3 CSV rows, got $csv_rows" >&2
    fi
    echo "=== END $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
  } > "$run_log_file" 2> "$run_dir/stderr.log"
}

export -f run_one
export OPENCLAW_RUN_CMD
export THINKING_LEVEL

find "$RUN_ROOT" -name prompt.md | sort | xargs -n 1 -P "$JOBS" bash -lc 'run_one "$0"'

echo "Completed arxiv MCP pre-experiment runs under: $RUN_ROOT"
