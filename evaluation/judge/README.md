# LLM Judge Pipeline

This directory contains the scripts used to extract claim-citation pairs from OpenClaw reports, build model-judge batches, aggregate judgments, and plot the final figures used in the presentation.

## Inputs

The main inputs are repaired reports from:

```text
runs/main_memory/M1_memory_on/P1/*/memory_on/output.raw.txt
runs/main_memory/M1_memory_on/P2/*/memory_on/output.raw.txt
runs/pre_refchecker_repair/*/*/refchecker_repair/output.raw.txt
```

The presentation paper-source snapshot is stored in:

```text
evaluation/judge/outputs/presentation_paper_sources.json
```

## Main Scripts

| Script | Purpose |
| --- | --- |
| `build_judge_inputs.py` | Parse reports and build claim-citation pairs plus batch prompts. |
| `run_deepseek_judge.py` | Run the LLM judge over prepared batches. Requires an API key. |
| `aggregate_judgments.py` | Aggregate JSONL judgments into error-rate tables. |
| `plot_*.py` | Generate presentation figures from aggregated CSV/JSON data. |
| `sync_presentation_papers.py` | Sync source-paper references used by the presentation judging workflow. |

## Rebuild Pattern

```bash
python3 evaluation/judge/build_judge_inputs.py --help
python3 evaluation/judge/run_deepseek_judge.py --help
python3 evaluation/judge/aggregate_judgments.py --help
```

Set credentials with:

```bash
# DeepSeek credential for the optional LLM-as-judge pass.
# Keep the real key in your shell or local profile; never commit it.
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"
```

No API keys or partial empty judge outputs are committed.

## Included Outputs

- `figures/*.png`: final plots used by `presentation/openclaw_deepresearch_overview.tex`.
- `outputs/**/summary.json`: batch construction summaries.
- `outputs/**/claim_citation_pairs.jsonl`: structured judge inputs.
- `outputs/**/batches/*.txt`: reproducible prompts sent to the judge model.

The `cache/` directory is ignored because it can be regenerated from source PDFs and reports.
The large local paper bundle under `presentation/main_memory/` is also ignored; regenerate it locally with `sync_presentation_papers.py` if you need to rebuild evidence snippets from PDFs.
