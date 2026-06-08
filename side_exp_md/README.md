# Side Experiment: Action Memory

This folder documents a small auxiliary experiment on an earlier action-memory design.

The side experiment is not the formal main memory experiment. It uses:

- `scripts/action_memory.jsonl`
- `scripts/retrieve.py`
- BM25 / `summary_bm25` retrieval
- fine-grained action records such as `fetch_paper` and `make_claim`

The formal main experiment instead uses:

- `runs/main_memory/M1_memory_on/_memory/active_memory.jsonl`
- `evaluation/main_experiments/scripts/retrieve_memory_context.py`
- TF-IDF-like lexical scoring over normalized `REFCHECKER_REPAIR_LOG` rows

## Included Report

`action_memory_effectiveness_report.md` summarizes:

- run1 no-memory baseline vs run2 with run1 action memory
- error-rate change from 28.2% to 5.1%
- three traceable improvement chains
- limitations caused by BM25 lexical retrieval and `web_fetch` truncation

Treat this as supporting evidence that structured error memory can be useful, not as a substitute for the formal M1 memory results.
