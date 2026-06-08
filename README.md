# OpenClaw DeepResearch Citation Consistency Evaluation

This repository contains a reproducible evaluation package for testing whether an OpenClaw-based scientific research agent produces conclusions whose cited sources do not sufficiently support the claim.

The project does not modify OpenClaw internals. It controls the experiment through prompts, skills, MCP/profile configuration, run scripts, structured logs, citation-standard validation, refchecker repair logs, and external judging scripts.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `citation-standard/` | OpenClaw skill for standardized claim-paper-source citations and a validator for CPS syntax. |
| `case paper/` | Small tracked test-case paper set used as reproducible source material. Future large paper drops are ignored. |
| `evaluation/pre_experiments/` | arXiv MCP and refchecker repair pre-experiment prompts, setup scripts, run manifests, and record tables. |
| `evaluation/main_experiments/` | Main memory experiment scripts, manifests, output inventory, and action-length figures. |
| `evaluation/judge/` | Claim-citation extraction, LLM judge batching/aggregation scripts, and result figures. |
| `runs/pre_arxiv/` | Completed arXiv MCP pre-experiment run artifacts. |
| `runs/pre_refchecker_repair/` | Completed refchecker repair pre-experiment artifacts; used as the practical no-memory baseline. |
| `runs/main_memory/M1_memory_on/` | Final memory-on main experiment artifacts for P1/P2, including per-run logs and shared memory JSONL. |
| `scripts/` | Side-experiment action-memory tools using BM25/summary_bm25 retrieval. |
| `side_exp_md/` | Action-memory side-experiment report. |
| `presentation/` | Final Beamer slides, figures, speaker notes, and defense QA pairs. |
| `docs/` | Design notes and experiment rationale. |

## Environment

Required local tools:

- OpenClaw installed locally.
- Python 3.10+.
- `bash`, `git`, `rg`.
- `xelatex` and `pdfinfo` if rebuilding the presentation.
- DeepSeek-compatible API key for LLM judging or OpenClaw runs.
- Brave search provider configured in OpenClaw for the experiment profiles.

Recommended environment variables:

```bash
# DeepSeek credential for OpenClaw runs and the optional LLM judge.
# Keep the real key in your shell or local profile; never commit it.
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"

# Local proxy used during these experiments on the author's machine.
# 127.0.0.1:7897 was the local Clash HTTP/HTTPS proxy endpoint.
export HTTPS_PROXY="http://127.0.0.1:7897"
export HTTP_PROXY="http://127.0.0.1:7897"

# Keep arXiv and local OpenClaw/MCP traffic out of the proxy.
# If your proxy breaks DeepSeek CONNECT requests, add api.deepseek.com here locally.
export NO_PROXY="arxiv.org,export.arxiv.org,localhost,127.0.0.1"
```

For OpenClaw runs, the scripts expect an `OPENCLAW_RUN_CMD` that reads `$PROMPT_FILE` and writes the agent output to stdout:

```bash
# The runners set OPENCLAW_PROFILE, SESSION_KEY, THINKING_LEVEL, and PROMPT_FILE.
export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 2400 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'
```

Use `JOBS=1` by default. Parallel execution caused web search, MCP, and DeepSeek timeout artifacts during development.

## Reproduction Entry Points

### 1. Validate Citation Syntax

```bash
python3 citation-standard/scripts/validate.py <report.md>
```

The expected citation form is documented in `citation-standard/references/cps-spec.md`.

### 2. arXiv MCP Pre-Experiment

```bash
bash evaluation/pre_experiments/scripts/prepare_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/preflight_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/setup_arxiv_profiles.sh
JOBS=1 SKIP_EXISTING=1 bash evaluation/pre_experiments/scripts/run_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/collect_arxiv_outputs.sh
```

Completed run artifacts are under `runs/pre_arxiv/`.

### 3. Refchecker Repair Pre-Experiment

```bash
bash evaluation/pre_experiments/scripts/prepare_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/preflight_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/setup_refchecker_repair_profiles.sh
JOBS=1 SKIP_EXISTING=1 bash evaluation/pre_experiments/scripts/run_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/collect_refchecker_repair_outputs.sh
```

Completed artifacts are under `runs/pre_refchecker_repair/`. These outputs are the practical no-memory baseline used in the final presentation.

### 4. Main Memory Experiment

The final project scope uses only `M1_memory_on` with two sequential passes:

```text
(C1 -> C2 -> C3 -> C4 -> C5) x 2 passes
```

Run or resume:

```bash
bash evaluation/main_experiments/scripts/prepare_main_memory_runs.sh
bash evaluation/main_experiments/scripts/preflight_main_memory_runs.sh
bash evaluation/main_experiments/scripts/setup_main_memory_profiles.sh

JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh

# Resume from a later run if needed:
MAIN_MEMORY_START_AT=P2_C3 JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh
```

The runner forces serial execution for memory-on runs because they share:

```text
runs/main_memory/M1_memory_on/_memory/active_memory.jsonl
```

### 5. Judge Pipeline

Build claim-citation inputs and aggregate LLM judgments:

```bash
python3 evaluation/judge/build_judge_inputs.py --help
python3 evaluation/judge/run_deepseek_judge.py --help
python3 evaluation/judge/aggregate_judgments.py --help
```

The repository includes generated figures and claim-citation input batches, but not API keys or incomplete/empty judge output files.
The large pass-specific evidence cache under `presentation/main_memory/` is intentionally not tracked; regenerate it locally with `evaluation/judge/sync_presentation_papers.py` before rebuilding judge snippets from PDFs.

### 6. Presentation

```bash
cd presentation
xelatex -interaction=nonstopmode -halt-on-error openclaw_deepresearch_overview.tex
xelatex -interaction=nonstopmode -halt-on-error openclaw_deepresearch_overview.tex
```

Then remove LaTeX build artifacts before committing.

## Final Experimental Scope

- Planning ablation was dropped. The final runs use OpenClaw default planning.
- Formal no-memory reruns were not completed due to time cost. The completed `pre_refchecker_repair` runs are used as a practical no-memory baseline.
- Main memory uses a structured JSONL memory derived only from `REFCHECKER_REPAIR_LOG`. It is injected as procedural caution, not scientific evidence.
- The side experiment in `side_exp_md/` uses a different action-memory design with BM25/summary_bm25. It is supporting evidence only and is not mixed with the formal M1 memory results.

## Reproducibility Notes

- Every OpenClaw run directory stores `run_manifest.json`, `prompt.md`, `output.raw.txt`, `stderr.log`, `run.log`, and profile audit files when available.
- Generated caches, aborted runs, personal reports, local demo outputs, and large local presentation paper copies are intentionally ignored.
- No API keys are stored in this repository. Use environment variables for credentials.
