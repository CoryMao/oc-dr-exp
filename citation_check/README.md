# Citation Check Utilities

This directory contains an earlier standalone citation-consistency checker. It is separate from the final `evaluation/judge/` pipeline but remains useful as a smoke-test and reference implementation for claim-citation parsing.

## Files

| File | Purpose |
| --- | --- |
| `parse_report.py` | Parse report sections, claims, citations, and references. |
| `pdf_extract.py` | Extract paper text snippets for cited sources. |
| `prompts.py` | Judge prompt templates and few-shot examples. |
| `check_citations.py` | Run the checker and write `results.json`. |
| `_smoke.json` / `results.json` | Small retained outputs for reproducibility checks. |

## Usage

```bash
export DEEPSEEK_API_KEY=...
python3 citation_check/check_citations.py --help
```

This utility expects local report and paper paths in the format documented in the script. For final presentation results, use `evaluation/judge/` instead.

## Notes

- `.cache/` and `__pycache__/` are intentionally ignored.
- API keys must be provided by environment variable or command-line argument and must not be committed.
