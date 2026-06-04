#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_arxiv"
OUT="$ROOT_DIR/evaluation/pre_experiments/arxiv_mcp_agent_outputs.csv"

header="case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note"
echo "$header" > "$OUT"

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  exit 1
fi

while IFS= read -r output_file; do
  grep -E '^[Cc][0-9]+,R[123],arxiv_(on|off),' "$output_file" >> "$OUT" || true
done < <(find "$RUN_ROOT" -name output.csv | sort)

echo "Wrote collected CSV rows to: $OUT"
echo "Rows including header: $(wc -l < "$OUT" | tr -d ' ')"
