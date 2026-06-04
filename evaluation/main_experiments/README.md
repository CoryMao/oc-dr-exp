# Main Memory Experiment

This folder contains the reproducible MVP setup for the formal OpenClaw memory experiment.

The experiment fixes planning to the OpenClaw default. For time budget reasons, the default runnable scope is now only:

```text
M1_memory_on: (C1 -> C2 -> C3 -> C4 -> C5) x 3 sequential passes
```

The no-memory baseline is not rerun by default. Use the completed `runs/pre_refchecker_repair` outputs as the practical no-memory baseline, or set `INCLUDE_NO_MEMORY=1` / `MAIN_MEMORY_CONDITION=all` to regenerate the formal M0 directories later.

The full planned comparison remains:

```text
M0_no_memory: 5 cases x 3 independent runs
M1_memory_on: (C1 -> C2 -> C3 -> C4 -> C5) x 3 sequential passes
```

Both conditions use the same report-generation prompt shape from the refchecker repair pre-experiment:

```text
ORIGINAL_REPORT -> REFCHECKER_REPAIR_LOG -> REPAIRED_REPORT -> RUN_SUMMARY
```

## Memory MVP

`M1_memory_on` uses a shared, auditable memory file:

```text
runs/main_memory/M1_memory_on/_memory/active_memory.jsonl
```

Only normalized rows extracted from `REFCHECKER_REPAIR_LOG` are written to this file. The retrieved memory is injected into the next prompt as procedural caution only. It is not evidence and must not be cited.

## Workflow

Prepare run directories and manifests:

```bash
bash evaluation/main_experiments/scripts/prepare_main_memory_runs.sh
bash evaluation/main_experiments/scripts/preflight_main_memory_runs.sh
```

By default this prepares/checks only `M1_memory_on`. To also prepare/check the formal M0 rerun:

```bash
INCLUDE_NO_MEMORY=1 bash evaluation/main_experiments/scripts/prepare_main_memory_runs.sh
MAIN_MEMORY_CONDITION=all bash evaluation/main_experiments/scripts/preflight_main_memory_runs.sh
```

Create or refresh OpenClaw profiles and workspaces:

```bash
bash evaluation/main_experiments/scripts/setup_main_memory_profiles.sh
```

By default setup refreshes only the shared `main-m1-memory-on` profile.

Run with the same proxy environment used in the pre-experiments:

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export NO_PROXY=arxiv.org,export.arxiv.org,localhost,127.0.0.1

export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 2400 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'

JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh
```

`JOBS` is forced to `1` by the runner because `M1_memory_on` is sequential and shares one memory file.

Collect a lightweight output inventory:

```bash
bash evaluation/main_experiments/scripts/collect_main_memory_outputs.sh
```

## Run Roots

```text
runs/main_memory/M0_no_memory/C1/R1/no_memory/
runs/main_memory/M1_memory_on/P1/C1/memory_on/
```

Each run directory stores:

```text
run_manifest.json
prompt.md
output.raw.txt
stderr.log
run.log
```

`M1_memory_on` also stores per-run memory artifacts:

```text
memory_context.md
memory_before.jsonl
memory_after.jsonl
```

Shared memory logs live under:

```text
runs/main_memory/M1_memory_on/_memory/
```
