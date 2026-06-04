#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROMPT_DIR="$ROOT_DIR/evaluation/pre_experiments/prompts/filled"
RUN_ROOT="${MAIN_MEMORY_RUN_ROOT:-$ROOT_DIR/runs/main_memory}"
INCLUDE_NO_MEMORY="${INCLUDE_NO_MEMORY:-0}"

case_topic() {
  case "$1" in
    1) printf '%s' "tool-augmented LLM agents versus prompting for complex coding tasks" ;;
    2) printf '%s' "recursive synthetic data, weak data, multimodal synthetic training, and model collapse" ;;
    3) printf '%s' "deep learning for protein-ligand docking, molecule generation, binding affinity, and benchmark leakage" ;;
    4) printf '%s' "human cognitive benchmarks, multimodal reasoning, and cross-scene hallucination" ;;
    5) printf '%s' "AI coding tools, experienced developer productivity, SWE-Bench Pro, and software engineering agents" ;;
    *) echo "Unknown case number: $1" >&2; return 1 ;;
  esac
}

write_manifest() {
  local manifest_file="$1"
  local experiment="$2"
  local condition="$3"
  local case_id="$4"
  local run_id="$5"
  local pass_id="$6"
  local topic="$7"
  local prompt_template="$8"
  local prompt_base_file="$9"
  local prompt_file="${10}"
  local prompt_sha="${11}"
  local template_sha="${12}"
  local profile_name="${13}"
  local workspace_dir="${14}"
  local expected_inputs="${15}"
  local memory_file="${16}"
  local retrieve_log_file="${17}"

  python3 - "$manifest_file" "$experiment" "$condition" "$case_id" "$run_id" "$pass_id" "$topic" "$prompt_template" "$prompt_base_file" "$prompt_file" "$prompt_sha" "$template_sha" "$profile_name" "$workspace_dir" "$expected_inputs" "$memory_file" "$retrieve_log_file" <<'PY'
import json
import os
import sys

(
    manifest_file,
    experiment,
    condition,
    case_id,
    run_id,
    pass_id,
    topic,
    prompt_template,
    prompt_base_file,
    prompt_file,
    prompt_sha,
    template_sha,
    profile_name,
    workspace_dir,
    expected_inputs,
    memory_file,
    retrieve_log_file,
) = sys.argv[1:18]

memory_enabled = condition == "memory_on"
manifest = {
    "experiment": experiment,
    "case_id": case_id,
    "run_id": run_id,
    "pass_id": pass_id,
    "condition": condition,
    "topic": topic,
    "prompt_template": prompt_template,
    "prompt_base_file": prompt_base_file,
    "prompt_file": prompt_file,
    "prompt_sha256": prompt_sha,
    "template_sha256": template_sha,
    "openclaw_profile": profile_name,
    "openclaw_state_dir": os.path.expanduser(f"~/.openclaw-{profile_name}"),
    "openclaw_workspace_dir": workspace_dir,
    "expected_workspace_inputs": expected_inputs,
    "memory": {
        "enabled": memory_enabled,
        "mode": "active_retrieval_plus_prompt_injection" if memory_enabled else "off",
        "memory_file": memory_file if memory_enabled else "",
        "retrieve_log_file": retrieve_log_file if memory_enabled else "",
        "top_k": 6,
        "source": "normalized_REF_CHECKER_REPAIR_LOG_rows_only" if memory_enabled else "",
    },
    "fixed_settings": {
        "memory": "on" if memory_enabled else "off",
        "memory_search": "explicit_jsonl_retrieval" if memory_enabled else "off",
        "startup_context": "off",
        "plan": "openclaw_default",
        "thinking": os.environ.get("EXPERIMENT_THINKING", "high"),
        "pdf_skill": "on",
        "citation-standard": "on",
        "web_search": "on:brave",
        "fs_workspace_only": True,
        "arxiv_mcp": "on:safe_wrapper",
        "refchecker": "on",
    },
    "output_contract": {
        "top_level_markers": [
            "# ORIGINAL_REPORT",
            "# REFCHECKER_REPAIR_LOG",
            "# REPAIRED_REPORT",
            "# RUN_SUMMARY",
        ],
        "repair_log_format": "jsonl",
        "run_summary_format": "json",
    },
}

with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

mkdir -p "$RUN_ROOT"
mkdir -p "$RUN_ROOT/M1_memory_on/_memory"
touch "$RUN_ROOT/M1_memory_on/_memory/active_memory.jsonl"
touch "$RUN_ROOT/M1_memory_on/_memory/retrieve_log.jsonl"

if [[ "$INCLUDE_NO_MEMORY" == "1" ]]; then
  for case_num in 1 2 3 4 5; do
    case_id="C${case_num}"
    topic="$(case_topic "$case_num")"
    template="$PROMPT_DIR/case${case_num}_refchecker_repair_prompt.md"

    if [[ ! -f "$template" ]]; then
      echo "Missing template: $template" >&2
      exit 1
    fi

    for run_num in 1 2 3; do
      run_id="R${run_num}"
      condition="no_memory"
      run_dir="$RUN_ROOT/M0_no_memory/${case_id}/${run_id}/${condition}"
      prompt_file="$run_dir/prompt.md"
      manifest_file="$run_dir/run_manifest.json"
      profile_name="$(printf 'main-m0-c%s-r%s-no-memory' "$case_num" "$run_num")"
      workspace_dir="$HOME/.openclaw-$profile_name/workspace"

      mkdir -p "$run_dir"
      sed "s/{run_id}/${run_id}/g" "$template" > "$prompt_file"

      prompt_hash="$(shasum -a 256 "$prompt_file" | awk '{print $1}')"
      template_hash="$(shasum -a 256 "$template" | awk '{print $1}')"

      write_manifest \
        "$manifest_file" \
        "main_memory_mvp" \
        "$condition" \
        "$case_id" \
        "$run_id" \
        "" \
        "$topic" \
        "$template" \
        "$prompt_file" \
        "$prompt_file" \
        "$prompt_hash" \
        "$template_hash" \
        "$profile_name" \
        "$workspace_dir" \
        "input_papers/case${case_num}" \
        "" \
        ""
    done
  done
fi

memory_file="$RUN_ROOT/M1_memory_on/_memory/active_memory.jsonl"
retrieve_log_file="$RUN_ROOT/M1_memory_on/_memory/retrieve_log.jsonl"
shared_profile="main-m1-memory-on"
shared_workspace="$HOME/.openclaw-$shared_profile/workspace"

for pass_num in 1 2 3; do
  pass_id="P${pass_num}"
  for case_num in 1 2 3 4 5; do
    case_id="C${case_num}"
    topic="$(case_topic "$case_num")"
    template="$PROMPT_DIR/case${case_num}_refchecker_repair_prompt.md"
    condition="memory_on"
    run_id="${pass_id}_${case_id}"
    run_dir="$RUN_ROOT/M1_memory_on/${pass_id}/${case_id}/${condition}"
    prompt_base_file="$run_dir/prompt.base.md"
    prompt_file="$run_dir/prompt.md"
    manifest_file="$run_dir/run_manifest.json"

    mkdir -p "$run_dir"
    sed "s/{run_id}/${run_id}/g" "$template" > "$prompt_base_file"

    prompt_hash="$(shasum -a 256 "$prompt_base_file" | awk '{print $1}')"
    template_hash="$(shasum -a 256 "$template" | awk '{print $1}')"

    write_manifest \
      "$manifest_file" \
      "main_memory_mvp" \
      "$condition" \
      "$case_id" \
      "$run_id" \
      "$pass_id" \
      "$topic" \
      "$template" \
      "$prompt_base_file" \
      "$prompt_file" \
      "$prompt_hash" \
      "$template_hash" \
      "$shared_profile" \
      "$shared_workspace" \
      "input_papers/case${case_num}" \
      "$memory_file" \
      "$retrieve_log_file"
  done
done

echo "Prepared main memory experiment runs under: $RUN_ROOT"
echo "Default active condition: memory_on"
echo "M1 manifest count: $(find "$RUN_ROOT/M1_memory_on" -name run_manifest.json | wc -l | tr -d ' ')"
if [[ -d "$RUN_ROOT/M0_no_memory" ]]; then
  echo "M0 prompt count: $(find "$RUN_ROOT/M0_no_memory" -name prompt.md | wc -l | tr -d ' ') (ignored unless INCLUDE_NO_MEMORY=1 or MAIN_MEMORY_CONDITION=all)"
else
  echo "M0 prompt count: 0"
fi
echo "M1 prompt base count: $(find "$RUN_ROOT/M1_memory_on" -name prompt.base.md | wc -l | tr -d ' ')"
