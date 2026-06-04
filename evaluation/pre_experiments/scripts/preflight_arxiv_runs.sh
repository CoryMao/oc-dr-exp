#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_arxiv"

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  echo "Run prepare_arxiv_runs.sh first." >&2
  exit 1
fi

expected=30
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
  if ! grep -q '"openclaw_profile": "pre-arxiv-' "$manifest"; then
    echo "Missing openclaw_profile in: $manifest" >&2
    missing_profile=1
  fi
done < <(find "$RUN_ROOT" -name run_manifest.json | sort)

if [[ "$missing_profile" != "0" ]]; then
  exit 1
fi

echo "Preflight PASS"
echo "Prompts: $prompt_count"
echo "Manifests: $manifest_count"
