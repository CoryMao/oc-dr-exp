# Pre-Experiment Record Tables

These tables are for the MCP tool pre-experiments. They are intentionally lightweight. The main experiment annotation schema can be designed later.

Prompt templates:

- `prompts/arxiv_mcp_pre_experiment_prompts.md`
- `prompts/refchecker_pre_experiment_prompts.md`
- `prompts/filled/arxiv_mcp_concrete_prompts.md`

## Configuration Control

Tool variables should be controlled by the OpenClaw/workspace configuration, not by prompt-only instructions.

Recommended pre-experiment profiles:

- `preexp_arxiv_off`: arxiv MCP disabled; mcp-refchecker disabled; memory disabled.
- `preexp_arxiv_on`: arxiv MCP enabled; mcp-refchecker disabled; memory disabled.
- `preexp_refchecker_off`: mcp-refchecker disabled; memory disabled.
- `preexp_refchecker_on`: mcp-refchecker enabled; memory disabled.

Record the actual profile or config file used for each run in the raw run log.

## arxiv_mcp_records.csv

Purpose: record whether `arxiv MCP` helps the agent autonomously select suitable [D], [E], and [F] papers.

Fill one row for each selected paper.

Run count:

```text
5 cases x 2 conditions x 3 runs x 3 selected papers = 90 rows
```

Columns:

- `case_id`: case label, such as `C1` to `C5`.
- `run_id`: run label, `R1`, `R2`, or `R3`.
- `condition`: `arxiv_off` or `arxiv_on`.
- `selected_tag`: `D`, `E`, or `F`.
- `paper_title`: title selected by the agent.
- `paper_id_or_url`: arXiv ID, DOI, URL, or other stable identifier.
- `year`: publication or preprint year.
- `full_text_available`: `yes` or `no`.
- `topic_relevance`: `0`, `1`, or `2`.
- `is_duplicate`: `yes` or `no`.
- `is_tangential`: `yes` or `no`.
- `valid_paper`: `yes` or `no`.
- `selection_note`: short human note explaining edge cases.

Relevance scale:

- `0`: irrelevant or off-topic.
- `1`: broadly related but not direct evidence for the report task.
- `2`: highly relevant and usable as direct evidence material.

Recommended validity rule:

```text
valid_paper = yes iff
topic_relevance = 2
and full_text_available = yes
and is_duplicate = no
and is_tangential = no
```

Minimum statistics:

```text
valid_paper_rate_per_run = valid selected papers / total selected papers
case_success_rate_per_run = cases with three valid selected papers / total cases
final_valid_paper_rate = mean(valid_paper_rate_per_run across R1-R3)
final_case_success_rate = mean(case_success_rate_per_run across R1-R3)
```

## refchecker_records.csv

Purpose: record whether `mcp-refchecker` helps detect claim-citation errors compared with a no-refchecker self-check.

Fill one row for each claim checked under each checker condition.

Run count: use three independent report batches, `R1`, `R2`, and `R3`, then average the metrics across runs.

Columns:

- `report_id`: stable report identifier.
- `case_id`: case label, such as `C1` to `C5`.
- `run_id`: run label, `R1`, `R2`, or `R3`.
- `claim_id`: claim identifier within the report.
- `checker_condition`: `no_refchecker` or `refchecker`.
- `human_error_exists`: `yes` or `no`.
- `human_error_type`: `unsupported_claim`, `overclaim`, `mis_citation`, `contradiction`, or `none`.
- `checker_flagged`: `yes` or `no`.
- `checker_error_type`: checker-predicted error type, or `none`.
- `checker_explanation`: short summary of the checker output.
- `human_judgment_note`: short human explanation.

Minimum statistics:

```text
error_detection_rate_per_run = true human errors flagged by checker / total human-confirmed errors
false_alarm_rate_per_run = checker flags rejected by human / total checker flags
final_error_detection_rate = mean(error_detection_rate_per_run across R1-R3)
final_false_alarm_rate = mean(false_alarm_rate_per_run across R1-R3)
```

Notes:

- Keep `citation-standard` fixed to ON when generating reports for the refchecker pre-experiment.
- Do not feed pre-experiment checker results back into memory.

## Running the arxiv MCP Pre-Experiment

The automation scripts prepare isolated run directories and can call OpenClaw in parallel once a concrete command is provided.

1. Prepare run directories:

```bash
bash evaluation/pre_experiments/scripts/prepare_arxiv_runs.sh
```

This creates:

```text
runs/pre_arxiv/C1/R1/arxiv_off/
runs/pre_arxiv/C1/R1/arxiv_on/
...
```

Each run directory contains:

- `prompt.md`: the filled prompt with `R1`, `R2`, or `R3` inserted.
- `run_manifest.json`: condition metadata and prompt/config hashes.

The manifest also assigns an isolated OpenClaw profile name such as:

```text
pre-arxiv-c1-r1-on
pre-arxiv-c1-r1-off
```

OpenClaw's global `--profile <name>` flag isolates state under `~/.openclaw-<name>`, so parallel runs should not share memory, sessions, or config state when each run uses its own profile.

2. Preflight check:

```bash
bash evaluation/pre_experiments/scripts/preflight_arxiv_runs.sh
```

3. Prepare isolated OpenClaw profiles:

```bash
bash evaluation/pre_experiments/scripts/setup_arxiv_profiles.sh
```

This copies the base OpenClaw config into each run profile and applies the experiment condition:

- `arxiv_on`: keeps only `mcp.servers.arxiv`.
- `arxiv_off`: removes all MCP servers.
- Both conditions keep `pdf`, `citation-standard`, and generic web search enabled.
- Generic web search is fixed to `brave` in all profiles.
- Memory-related plugins such as `active-memory`, `memory-core`, and `memory-wiki` are removed from the pre-experiment profiles.
- Agent memory search and startup context are disabled.
- Each profile uses an isolated workspace under `~/.openclaw-<profile>/workspace`.
- Filesystem tools are restricted to the profile-local workspace.
- Thinking is fixed to `medium` by default. Override with `EXPERIMENT_THINKING=low|medium|high|...` only if the whole experiment uses that same value.
- `citation-standard` is installed into each profile so `openclaw --profile ...` can load it.

Each run directory also receives `openclaw_profile_audit.md`, which records the effective config path, MCP servers, skill entries, skill list, and skill check result for that profile.

4. Run with OpenClaw:

Set `OPENCLAW_RUN_CMD` to the actual command that reads `$PROMPT_FILE` and writes the agent output to stdout. The runner saves raw output and extracts CSV rows into `output.csv`.

```bash
export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'
JOBS=1 bash evaluation/pre_experiments/scripts/run_arxiv_runs.sh
```

Use serial execution (`JOBS=1`) by default. Higher parallelism can trigger web search and MCP timeout artifacts; record it as a run deviation if used.

Before a real batch run, audit a prepared profile:

```bash
AUDIT_OUT_DIR=runs/pre_arxiv/C1/R1/arxiv_on \
  bash evaluation/pre_experiments/scripts/audit_openclaw_profile.sh pre-arxiv-c1-r1-on
```

The audit records the active config file, config validation result, MCP list, MCP config, skill list, and skill readiness.

5. Collect outputs:

```bash
bash evaluation/pre_experiments/scripts/collect_arxiv_outputs.sh
```

This writes:

```text
evaluation/pre_experiments/arxiv_mcp_agent_outputs.csv
```

Human annotation can then be copied into `arxiv_mcp_records.csv`.
