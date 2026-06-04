#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROMPT_DIR="$ROOT_DIR/evaluation/pre_experiments/prompts/filled"
RUN_ROOT="$ROOT_DIR/runs/pre_arxiv"

mkdir -p "$RUN_ROOT"

for case_num in 1 2 3 4 5; do
  case_id="C${case_num}"
  for run_id in R1 R2 R3; do
    for condition in arxiv_off arxiv_on; do
      template="$PROMPT_DIR/case${case_num}_${condition}_prompt.md"
      run_dir="$RUN_ROOT/${case_id}/${run_id}/${condition}"
      prompt_file="$run_dir/prompt.md"
      manifest_file="$run_dir/run_manifest.json"

      if [[ ! -f "$template" ]]; then
        echo "Missing template: $template" >&2
        exit 1
      fi

      mkdir -p "$run_dir"
      sed "s/{run_id}/${run_id}/g" "$template" > "$prompt_file"

      config_path=""
      if [[ "$condition" == "arxiv_on" ]]; then
        config_path="${ARXIV_ON_CONFIG:-}"
      else
        config_path="${ARXIV_OFF_CONFIG:-}"
      fi

      case_profile="$(printf '%s' "$case_id" | tr '[:upper:]' '[:lower:]')"
      run_profile="$(printf '%s' "$run_id" | tr '[:upper:]' '[:lower:]')"
      profile_name="pre-arxiv-${case_profile}-${run_profile}"
      if [[ "$condition" == "arxiv_on" ]]; then
        profile_name="${profile_name}-on"
      else
        profile_name="${profile_name}-off"
      fi
      workspace_dir="$HOME/.openclaw-$profile_name/workspace"

      prompt_hash="$(shasum -a 256 "$prompt_file" | awk '{print $1}')"
      template_hash="$(shasum -a 256 "$template" | awk '{print $1}')"
      config_hash=""
      if [[ -n "$config_path" && -f "$config_path" ]]; then
        config_hash="$(shasum -a 256 "$config_path" | awk '{print $1}')"
      fi

      cat > "$manifest_file" <<EOF
{
  "experiment": "arxiv_mcp_pre_experiment",
  "case_id": "$case_id",
  "run_id": "$run_id",
  "condition": "$condition",
  "prompt_template": "$template",
  "prompt_file": "$prompt_file",
  "prompt_sha256": "$prompt_hash",
  "template_sha256": "$template_hash",
  "config_path": "$config_path",
  "config_sha256": "$config_hash",
  "openclaw_profile": "$profile_name",
  "openclaw_state_dir": "$HOME/.openclaw-$profile_name",
  "openclaw_workspace_dir": "$workspace_dir",
  "fixed_settings": {
    "memory": "off",
    "memory_search": "off",
    "startup_context": "off",
    "plan": "default_minimal",
    "thinking": "${EXPERIMENT_THINKING:-high}",
    "pdf_skill": "on",
    "citation-standard": "on",
    "web_search": "on:brave",
    "fs_workspace_only": true,
    "refchecker": "off"
  },
  "variable": {
    "arxiv_mcp": "$condition"
  }
}
EOF
    done
  done
done

echo "Prepared arxiv MCP pre-experiment runs under: $RUN_ROOT"
echo "Run count: $(find "$RUN_ROOT" -name prompt.md | wc -l | tr -d ' ')"
