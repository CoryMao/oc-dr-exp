#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_refchecker_repair"
JOBS="${JOBS:-1}"
THINKING_LEVEL="${EXPERIMENT_THINKING:-high}"
SKIP_EXISTING="${SKIP_EXISTING:-0}"
SESSION_KEY_SUFFIX="${SESSION_KEY_SUFFIX:-}"

if [[ -z "${OPENCLAW_RUN_CMD:-}" ]]; then
  cat >&2 <<'EOF'
OPENCLAW_RUN_CMD is not set.

Set it to a shell command that reads the prompt from $PROMPT_FILE and writes
the agent output to stdout. The runner exports:

  RUN_DIR
  PROMPT_FILE
  MANIFEST_FILE
  RAW_OUTPUT_FILE
  CONDITION
  CASE_ID
  RUN_ID
  OPENCLAW_PROFILE
  SESSION_KEY
  SESSION_KEY_SUFFIX
  THINKING_LEVEL

Example shape:

  export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 1800 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'

Then run:

  JOBS=1 bash evaluation/pre_experiments/scripts/run_refchecker_repair_runs.sh
EOF
  exit 1
fi

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  echo "Run prepare_refchecker_repair_runs.sh first." >&2
  exit 1
fi

run_one() {
  local prompt_file="$1"
  local run_dir manifest_file raw_output_file run_log_file condition case_id run_id openclaw_profile session_key markers_ok command_status
  run_dir="$(dirname "$prompt_file")"
  manifest_file="$run_dir/run_manifest.json"
  raw_output_file="$run_dir/output.raw.txt"
  run_log_file="$run_dir/run.log"
  condition="$(basename "$run_dir")"
  run_id="$(basename "$(dirname "$run_dir")")"
  case_id="$(basename "$(dirname "$(dirname "$run_dir")")")"
  openclaw_profile="$(grep -E '"openclaw_profile":' "$manifest_file" | sed -E 's/.*"openclaw_profile": "([^"]+)".*/\1/')"
  session_key="refchecker-repair-pre-${case_id}-${run_id}${SESSION_KEY_SUFFIX}"

  if [[ "$SKIP_EXISTING" == "1" && -f "$run_log_file" && -f "$raw_output_file" ]] \
    && grep -q '^=== END ' "$run_log_file" \
    && grep -q '^markers_ok=yes$' "$run_log_file" \
    && grep -Eq '^# ORIGINAL_REPORT' "$raw_output_file" \
    && grep -Eq '^# REFCHECKER_REPAIR_LOG' "$raw_output_file" \
    && grep -Eq '^# REPAIRED_REPORT' "$raw_output_file" \
    && grep -Eq '^# RUN_SUMMARY' "$raw_output_file" \
    && ! grep -Eq 'Request timed out|Request was aborted|FailoverError|No API key found|MCP error -32000|MCP error -32001' "$raw_output_file"; then
    echo "Skipping existing completed run: $prompt_file"
    return 0
  fi

  export RUN_DIR="$run_dir"
  export PROMPT_FILE="$prompt_file"
  export MANIFEST_FILE="$manifest_file"
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
    set +e
    bash -lc "$OPENCLAW_RUN_CMD" > "$raw_output_file"
    command_status="$?"
    set -e
    echo "command_status=$command_status"
    markers_ok="yes"
    if [[ "$command_status" != "0" ]]; then
      markers_ok="no"
      echo "WARNING: OpenClaw command exited with status $command_status" >&2
    fi
    for marker in '^# ORIGINAL_REPORT' '^# REFCHECKER_REPAIR_LOG' '^# REPAIRED_REPORT' '^# RUN_SUMMARY'; do
      if ! grep -Eq "$marker" "$raw_output_file"; then
        markers_ok="no"
        echo "WARNING: missing marker $marker" >&2
      fi
    done
    if grep -Eq 'Request timed out|Request was aborted|FailoverError|No API key found|MCP error -32000|MCP error -32001' "$raw_output_file"; then
      markers_ok="no"
      echo "WARNING: raw output contains hard failure pattern" >&2
    fi
    echo "markers_ok=$markers_ok"
    echo "=== END $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
  } > "$run_log_file" 2> "$run_dir/stderr.log"
}

export -f run_one
export OPENCLAW_RUN_CMD
export THINKING_LEVEL
export SKIP_EXISTING
export SESSION_KEY_SUFFIX

if [[ "$#" -gt 0 ]]; then
  printf '%s\n' "$@" | xargs -n 1 -P "$JOBS" bash -lc 'run_one "$0"'
else
  find "$RUN_ROOT" -name prompt.md | sort | xargs -n 1 -P "$JOBS" bash -lc 'run_one "$0"'
fi

echo "Completed refchecker repair pre-experiment runs under: $RUN_ROOT"
