# Pre-Experiment Record Tables

These tables are for the MCP tool pre-experiments. They are intentionally lightweight. The main experiment annotation schema can be designed later.

Prompt templates:

- `prompts/arxiv_mcp_pre_experiment_prompts.md`
- `prompts/refchecker_pre_experiment_prompts.md`
- `prompts/refchecker_repair_pre_experiment_prompt.md`
- `prompts/filled/case*_arxiv_*_prompt.md`
- `prompts/filled/case*_refchecker_repair_prompt.md`

## Configuration Control

Tool variables should be controlled by the OpenClaw/workspace configuration, not by prompt-only instructions.

Recommended pre-experiment profiles:

- `preexp_arxiv_off`: arxiv MCP disabled; mcp-refchecker disabled; memory disabled.
- `preexp_arxiv_on`: arxiv MCP enabled; mcp-refchecker disabled; memory disabled.
- `pre-refchecker-c*-r*-repair`: arxiv MCP enabled; mcp-refchecker enabled; memory disabled; isolated workspace.

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
- Thinking is fixed to `high` by default. Override with `EXPERIMENT_THINKING=low|medium|high|...` only if the whole experiment uses that same value.
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

## Running the refchecker Repair Pre-Experiment

This is the generation-phase repair pre-experiment. Each run asks the agent to produce:

1. `ORIGINAL_REPORT`: the frozen first report before refchecker.
2. `REFCHECKER_REPAIR_LOG`: JSONL records for reference metadata checks and claim-citation checks.
3. `REPAIRED_REPORT`: the report after refchecker-informed repair.
4. `RUN_SUMMARY`: machine-readable counts for the run.

Run count:

```text
5 cases x 3 runs x 1 condition = 15 OpenClaw runs
```

The fixed configuration is:

- `pdf` skill: on.
- `citation-standard` skill: on.
- `arxiv MCP`: on.
- `mcp-refchecker`: on.
- Web search: on, provider fixed to `brave`.
- Memory, memory search, active memory, and startup context: off.
- Filesystem tools: restricted to each profile's isolated workspace.
- Thinking: `high` by default.

Important limitation: `mcp-refchecker` verifies citation metadata against academic publication databases. It does not directly decide whether a cited paragraph supports a report claim. The repair prompt therefore requires two checks: refchecker for metadata and source-reading for claim support.

1. Prepare run directories:

```bash
bash evaluation/pre_experiments/scripts/prepare_refchecker_repair_runs.sh
```

This creates:

```text
runs/pre_refchecker_repair/C1/R1/refchecker_repair/
runs/pre_refchecker_repair/C1/R2/refchecker_repair/
...
```

Each run directory contains:

- `prompt.md`: the filled prompt.
- `run_manifest.json`: condition metadata, prompt hashes, profile name, fixed settings, and expected output markers.

2. Preflight check:

```bash
bash evaluation/pre_experiments/scripts/preflight_refchecker_repair_runs.sh
```

3. Prepare isolated OpenClaw profiles:

```bash
bash evaluation/pre_experiments/scripts/setup_refchecker_repair_profiles.sh
```

This creates one profile per run, such as:

```text
pre-refchecker-c1-r1-repair
```

For each profile, the setup script:

- Copies base auth from `~/.openclaw/agents/main/agent/auth-profiles.json`.
- Pins arxiv MCP to a Python interpreter that can import `arxiv_mcp_server`.
- Launches arxiv MCP through `scripts/openclaw_arxiv_mcp_safe.py`.
- Pins refchecker MCP to the `mcp-refchecker` console script.
- Installs `citation-standard`.
- Copies the case PDFs into the profile workspace under `input_papers/caseN/`.
- Writes `openclaw_profile_audit.md` and `openclaw_profile_audit.stderr.log` into the run directory.

The arxiv safe wrapper keeps upstream tool names unchanged but adds experiment safeguards:

- Uses `arxiv.org/abs/<id>` for `get_abstract`, avoiding `export.arxiv.org` where possible.
- Uses direct `arxiv.org/pdf/<id>` plus local `pdftotext` for PDF fallback, avoiding export API metadata lookup during download.
- Disables best-effort semantic indexing after download, which otherwise makes extra export API calls.
- Gives `search_papers` a short export API timeout and returns a warning payload instead of letting OpenClaw kill the MCP connection.
- Caps `download_paper` and `read_paper` returned content with `ARXIV_MCP_CONTENT_CHAR_LIMIT=35000` by default; full paper text remains cached in the profile workspace.

This wrapper was added because local diagnostics showed `arxiv.org/html` and `arxiv.org/pdf` were reachable, while `export.arxiv.org/api/query` returned HTTP 429 or read timed out. Without the wrapper, OpenClaw saw arxiv MCP timeout/connection-closed errors and later `download_paper` calls returned `Not connected`.

4. Run a smoke test:

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export NO_PROXY=arxiv.org,export.arxiv.org,localhost,127.0.0.1
export https_proxy="$HTTPS_PROXY"
export http_proxy="$HTTP_PROXY"
export no_proxy="$NO_PROXY"

export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 1800 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'

JOBS=1 bash evaluation/pre_experiments/scripts/run_refchecker_repair_runs.sh \
  runs/pre_refchecker_repair/C1/R1/refchecker_repair/prompt.md
```

5. Run the full batch:

```bash
SKIP_EXISTING=1 JOBS=1 bash evaluation/pre_experiments/scripts/run_refchecker_repair_runs.sh
```

Use serial execution (`JOBS=1`) by default. This experiment combines arxiv search, PDF reading, web fetch, and refchecker database calls; parallelism can create tool timeout artifacts.

If a batch is interrupted by model billing/auth failure, keep `SKIP_EXISTING=1`: runs with `markers_ok=yes` and all four output markers will be skipped, while failed runs with `markers_ok=no` will be retried.

6. Collect output status:

```bash
bash evaluation/pre_experiments/scripts/collect_refchecker_repair_outputs.sh
```

This writes:

```text
evaluation/pre_experiments/refchecker_repair_agent_outputs.csv
```

Human annotation can then be copied into `refchecker_repair_records.csv`.
