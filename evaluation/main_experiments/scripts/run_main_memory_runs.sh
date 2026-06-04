#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="${MAIN_MEMORY_RUN_ROOT:-$ROOT_DIR/runs/main_memory}"
TARGET_CONDITION="${MAIN_MEMORY_CONDITION:-memory_on}"
THINKING_LEVEL="${EXPERIMENT_THINKING:-high}"
SKIP_EXISTING="${SKIP_EXISTING:-0}"
SESSION_KEY_SUFFIX="${SESSION_KEY_SUFFIX:-}"
JOBS="${JOBS:-1}"

if [[ "$JOBS" != "1" ]]; then
  echo "WARNING: forcing JOBS=1 because memory_on runs share active_memory.jsonl and must be sequential." >&2
  JOBS=1
fi

if [[ -z "${OPENCLAW_RUN_CMD:-}" ]]; then
  cat >&2 <<'EOF'
OPENCLAW_RUN_CMD is not set.

Set it to a shell command that reads the prompt from $PROMPT_FILE and writes
the agent output to stdout. The runner exports:

  RUN_DIR
  PROMPT_FILE
  PROMPT_BASE_FILE
  MANIFEST_FILE
  RAW_OUTPUT_FILE
  CONDITION
  CASE_ID
  RUN_ID
  PASS_ID
  OPENCLAW_PROFILE
  SESSION_KEY
  THINKING_LEVEL
  MEMORY_FILE
  MEMORY_CONTEXT_FILE

Example:

  export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 2400 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'

Then run:

  JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh
EOF
  exit 1
fi

[[ -d "$RUN_ROOT" ]] || { echo "Run root does not exist: $RUN_ROOT" >&2; exit 1; }

resolve_manifest() {
  local item="$1"
  if [[ -f "$item" && "$(basename "$item")" == "run_manifest.json" ]]; then
    printf '%s\n' "$item"
  elif [[ -f "$item" ]]; then
    printf '%s\n' "$(dirname "$item")/run_manifest.json"
  elif [[ -d "$item" ]]; then
    printf '%s\n' "$item/run_manifest.json"
  else
    printf '%s\n' "$item"
  fi
}

line_count() {
  local file="$1"
  if [[ -f "$file" ]]; then
    awk 'NF {count++} END {print count+0}' "$file"
  else
    printf '0\n'
  fi
}

markers_ok_for_output() {
  local raw="$1"
  local stderr_file="$2"
  [[ -f "$raw" ]] || return 1
  grep -Eq '^# ORIGINAL_REPORT' "$raw" || return 1
  grep -Eq '^# REFCHECKER_REPAIR_LOG' "$raw" || return 1
  grep -Eq '^# REPAIRED_REPORT' "$raw" || return 1
  grep -Eq '^# RUN_SUMMARY' "$raw" || return 1
  if grep -Eq 'Request timed out|Request was aborted|FailoverError|No API key found|MCP error -32000|MCP error -32001' "$raw" "$stderr_file" 2>/dev/null; then
    return 1
  fi
  return 0
}

run_one_manifest() {
  local manifest_file="$1"
  [[ -f "$manifest_file" ]] || { echo "Missing manifest: $manifest_file" >&2; return 1; }

  eval "$(
    python3 - "$manifest_file" <<'PY'
import json
import shlex
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
memory = data.get("memory") or {}
fields = {
    "condition": data["condition"],
    "case_id": data["case_id"],
    "run_id": data["run_id"],
    "pass_id": data.get("pass_id", ""),
    "prompt_file": data["prompt_file"],
    "prompt_base_file": data["prompt_base_file"],
    "openclaw_profile": data["openclaw_profile"],
    "topic": data.get("topic", ""),
    "memory_file": memory.get("memory_file", ""),
    "retrieve_log_file": memory.get("retrieve_log_file", ""),
    "top_k": str(memory.get("top_k", 6)),
}
for key, value in fields.items():
    print(f"{key}={shlex.quote(str(value))}")
PY
  )"

  if [[ "$TARGET_CONDITION" != "all" && "$condition" != "$TARGET_CONDITION" ]]; then
    echo "Skipping condition=$condition due to MAIN_MEMORY_CONDITION=$TARGET_CONDITION: $manifest_file"
    return 0
  fi

  local run_dir raw_output_file run_log_file stderr_file session_key memory_context_file memory_before_file memory_after_file memory_extract_report
  run_dir="$(dirname "$manifest_file")"
  raw_output_file="$run_dir/output.raw.txt"
  run_log_file="$run_dir/run.log"
  stderr_file="$run_dir/stderr.log"
  memory_context_file="$run_dir/memory_context.md"
  memory_before_file="$run_dir/memory_before.jsonl"
  memory_after_file="$run_dir/memory_after.jsonl"
  memory_extract_report="$run_dir/memory_extract_report.json"

  if [[ "$condition" == "memory_on" ]]; then
    session_key="main-memory-${pass_id}-${case_id}${SESSION_KEY_SUFFIX}"
  else
    session_key="main-no-memory-${case_id}-${run_id}${SESSION_KEY_SUFFIX}"
  fi

  if [[ "$SKIP_EXISTING" == "1" && -f "$run_log_file" && -f "$raw_output_file" ]] \
    && grep -q '^=== END ' "$run_log_file" \
    && grep -q '^markers_ok=yes$' "$run_log_file" \
    && markers_ok_for_output "$raw_output_file" "$stderr_file"; then
    echo "Skipping existing completed run: $manifest_file"
    return 0
  fi

  if [[ "$condition" == "memory_on" ]]; then
    mkdir -p "$(dirname "$memory_file")"
    touch "$memory_file" "$retrieve_log_file"
    cp "$memory_file" "$memory_before_file"
    python3 "$ROOT_DIR/evaluation/main_experiments/scripts/retrieve_memory_context.py" \
      --memory-file "$memory_file" \
      --query "$case_id $topic citation metadata support overclaim scope_error refchecker repair CPS" \
      --case-id "$case_id" \
      --pass-id "$pass_id" \
      --run-id "$run_id" \
      --top-k "$top_k" \
      --out "$memory_context_file" \
      --log-file "$retrieve_log_file" \
      > "$run_dir/retrieve.stdout.log"
    cat "$memory_context_file" "$prompt_base_file" > "$prompt_file"
  else
    memory_file=""
    memory_context_file=""
  fi

  export RUN_DIR="$run_dir"
  export PROMPT_FILE="$prompt_file"
  export PROMPT_BASE_FILE="$prompt_base_file"
  export MANIFEST_FILE="$manifest_file"
  export RAW_OUTPUT_FILE="$raw_output_file"
  export CONDITION="$condition"
  export CASE_ID="$case_id"
  export RUN_ID="$run_id"
  export PASS_ID="$pass_id"
  export OPENCLAW_PROFILE="$openclaw_profile"
  export SESSION_KEY="$session_key"
  export THINKING_LEVEL="$THINKING_LEVEL"
  export MEMORY_FILE="$memory_file"
  export MEMORY_CONTEXT_FILE="$memory_context_file"

  {
    echo "=== START $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
    echo "condition=$CONDITION case_id=$CASE_ID run_id=$RUN_ID pass_id=$PASS_ID"
    echo "openclaw_profile=$OPENCLAW_PROFILE session_key=$SESSION_KEY"
    echo "thinking=$THINKING_LEVEL"
    if [[ "$condition" == "memory_on" ]]; then
      echo "memory_file=$MEMORY_FILE"
      echo "memory_records_before=$(line_count "$memory_before_file")"
      echo "memory_context_file=$MEMORY_CONTEXT_FILE"
    fi

    set +e
    bash -lc "$OPENCLAW_RUN_CMD" > "$raw_output_file"
    local command_status="$?"
    set -e

    echo "command_status=$command_status"
    local markers_ok="yes"
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
    if grep -Eq 'Request timed out|Request was aborted|FailoverError|No API key found|MCP error -32000|MCP error -32001' "$raw_output_file" "$stderr_file" 2>/dev/null; then
      markers_ok="no"
      echo "WARNING: output contains hard failure pattern" >&2
    fi

    if [[ "$condition" == "memory_on" && "$markers_ok" == "yes" ]]; then
      python3 "$ROOT_DIR/evaluation/main_experiments/scripts/extract_refchecker_memory.py" \
        --output-file "$raw_output_file" \
        --manifest-file "$manifest_file" \
        --memory-file "$MEMORY_FILE" \
        --report-file "$memory_extract_report"
      cp "$MEMORY_FILE" "$memory_after_file"
      echo "memory_records_after=$(line_count "$memory_after_file")"
    elif [[ "$condition" == "memory_on" ]]; then
      cp "$MEMORY_FILE" "$memory_after_file"
      echo "memory_records_after=$(line_count "$memory_after_file")"
      echo "WARNING: skipped memory writeback because markers_ok=$markers_ok" >&2
    fi

    echo "markers_ok=$markers_ok"
    echo "=== END $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
  } > "$run_log_file" 2> "$stderr_file"
}

if [[ "$#" -gt 0 ]]; then
  for item in "$@"; do
    run_one_manifest "$(resolve_manifest "$item")"
  done
else
  if [[ "$TARGET_CONDITION" == "memory_on" ]]; then
    manifest_root="$RUN_ROOT/M1_memory_on"
  else
    manifest_root="$RUN_ROOT"
  fi
  while IFS= read -r manifest; do
    run_one_manifest "$manifest"
  done < <(find "$manifest_root" -name run_manifest.json | sort)
fi

echo "Completed main memory experiment runs under: $RUN_ROOT"
