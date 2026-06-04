#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROMPT_DIR="$ROOT_DIR/evaluation/pre_experiments/prompts/filled"
RUN_ROOT="$ROOT_DIR/runs/pre_refchecker_repair"

mkdir -p "$RUN_ROOT"

for case_num in 1 2 3 4 5; do
  case_id="C${case_num}"
  template="$PROMPT_DIR/case${case_num}_refchecker_repair_prompt.md"

  if [[ ! -f "$template" ]]; then
    echo "Missing template: $template" >&2
    exit 1
  fi

  for run_id in R1 R2 R3; do
    condition="refchecker_repair"
    run_dir="$RUN_ROOT/${case_id}/${run_id}/${condition}"
    prompt_file="$run_dir/prompt.md"
    manifest_file="$run_dir/run_manifest.json"

    mkdir -p "$run_dir"
    sed "s/{run_id}/${run_id}/g" "$template" > "$prompt_file"

    case_profile="$(printf '%s' "$case_id" | tr '[:upper:]' '[:lower:]')"
    run_profile="$(printf '%s' "$run_id" | tr '[:upper:]' '[:lower:]')"
    profile_name="pre-refchecker-${case_profile}-${run_profile}-repair"
    workspace_dir="$HOME/.openclaw-$profile_name/workspace"

    prompt_hash="$(shasum -a 256 "$prompt_file" | awk '{print $1}')"
    template_hash="$(shasum -a 256 "$template" | awk '{print $1}')"

    python3 - "$manifest_file" <<PY
import json
import os
import sys

manifest_file = sys.argv[1]
manifest = {
    "experiment": "refchecker_repair_pre_experiment",
    "case_id": "$case_id",
    "run_id": "$run_id",
    "condition": "$condition",
    "prompt_template": "$template",
    "prompt_file": "$prompt_file",
    "prompt_sha256": "$prompt_hash",
    "template_sha256": "$template_hash",
    "openclaw_profile": "$profile_name",
    "openclaw_state_dir": os.path.expanduser("~/.openclaw-$profile_name"),
    "openclaw_workspace_dir": "$workspace_dir",
    "expected_workspace_inputs": "input_papers/case${case_num}",
    "fixed_settings": {
        "memory": "off",
        "memory_search": "off",
        "startup_context": "off",
        "plan": "default_minimal",
        "thinking": os.environ.get("EXPERIMENT_THINKING", "high"),
        "pdf_skill": "on",
        "citation-standard": "on",
        "web_search": "on:brave",
        "fs_workspace_only": True,
        "arxiv_mcp": "on",
        "refchecker": "on"
    },
    "variable": {
        "refchecker_repair": "on"
    },
    "output_contract": {
        "top_level_markers": [
            "# ORIGINAL_REPORT",
            "# REFCHECKER_REPAIR_LOG",
            "# REPAIRED_REPORT",
            "# RUN_SUMMARY"
        ],
        "repair_log_format": "jsonl",
        "run_summary_format": "json"
    }
}
with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write("\\n")
PY
  done
done

echo "Prepared refchecker repair pre-experiment runs under: $RUN_ROOT"
echo "Run count: $(find "$RUN_ROOT" -name prompt.md | wc -l | tr -d ' ')"
