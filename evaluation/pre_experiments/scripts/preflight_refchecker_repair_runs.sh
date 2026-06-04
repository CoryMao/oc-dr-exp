#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_refchecker_repair"
CASE_PAPER_DIR="$ROOT_DIR/case paper"

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  echo "Run prepare_refchecker_repair_runs.sh first." >&2
  exit 1
fi

expected=15
prompt_count="$(find "$RUN_ROOT" -name prompt.md | wc -l | tr -d ' ')"
manifest_count="$(find "$RUN_ROOT" -name run_manifest.json | wc -l | tr -d ' ')"

if [[ "$prompt_count" != "$expected" ]]; then
  echo "Expected $expected prompts, found $prompt_count" >&2
  exit 1
fi

if [[ "$manifest_count" != "$expected" ]]; then
  echo "Expected $expected manifests, found $manifest_count" >&2
  exit 1
fi

missing_run_id=0
while IFS= read -r prompt; do
  if grep -q "{run_id}" "$prompt"; then
    echo "Unexpanded run_id placeholder in: $prompt" >&2
    missing_run_id=1
  fi
done < <(find "$RUN_ROOT" -name prompt.md | sort)

if [[ "$missing_run_id" != "0" ]]; then
  exit 1
fi

missing_profile=0
while IFS= read -r manifest; do
  if ! grep -q '"openclaw_profile": "pre-refchecker-' "$manifest"; then
    echo "Missing openclaw_profile in: $manifest" >&2
    missing_profile=1
  fi
  if ! grep -q '"refchecker": "on"' "$manifest"; then
    echo "Manifest does not enable refchecker: $manifest" >&2
    missing_profile=1
  fi
  if ! grep -q '"arxiv_mcp": "on"' "$manifest"; then
    echo "Manifest does not enable arxiv MCP: $manifest" >&2
    missing_profile=1
  fi
done < <(find "$RUN_ROOT" -name run_manifest.json | sort)

if [[ "$missing_profile" != "0" ]]; then
  exit 1
fi

missing_pdf=0
for case_num in 1 2 3 4 5; do
  pdf_count="$(find "$CASE_PAPER_DIR/case${case_num}" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
  if [[ "$pdf_count" != "3" ]]; then
    echo "Expected 3 PDFs for case${case_num}, found $pdf_count" >&2
    missing_pdf=1
  fi
done

if [[ "$missing_pdf" != "0" ]]; then
  exit 1
fi

echo "Preflight PASS"
echo "Prompts: $prompt_count"
echo "Manifests: $manifest_count"
