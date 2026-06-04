# OpenClaw Memory MVP Main Experiment Design

## Decision

The formal main experiment will use the default OpenClaw planning behavior only. Planning is no longer an experimental variable.

The memory comparison is reduced to two conditions:

```text
M0 no_memory
M1 memory_on
```

There is no separate passive-memory-only group. The `memory_on` condition combines active retrieval with passive prompt injection, using a small, auditable memory file derived only from refchecker repair logs.

## Fixed Stack

All main-experiment runs use the same validated tool stack:

```text
model = Deepseek v4 Pro
planning = OpenClaw default
pdf skill = on
citation-standard skill = on
arxiv MCP = on
mcp-refchecker = on
web search = Brave
thinking = high
case order = C1 -> C2 -> C3 -> C4 -> C5
```

The arxiv MCP should use the safe wrapper introduced during the refchecker repair pre-experiment, because local diagnostics showed that `export.arxiv.org/api/query` can return HTTP 429 or read timeout while `arxiv.org/abs`, `arxiv.org/html`, and `arxiv.org/pdf` remain usable.

## Main Matrix

### M0: no_memory

`M0` is equivalent in behavior to the current `pre_refchecker_repair` setup:

```text
5 cases x 3 independent runs = 15 outputs
```

Each run uses an isolated OpenClaw profile, workspace, and session key. All memory plugins, memory search, startup context, and memory writeback are disabled.

### M1: memory_on

`M1` uses one shared memory state across the fixed sequential order:

```text
Pass 1: C1 -> C2 -> C3 -> C4 -> C5
Pass 2: C1 -> C2 -> C3 -> C4 -> C5
Pass 3: C1 -> C2 -> C3 -> C4 -> C5

Total = 5 cases x 3 passes = 15 outputs
```

The memory state is shared across all 15 `M1` runs. Each case should still use a new session key, so improvement cannot be explained by direct chat-history continuation.

## Memory Scope

The MVP memory source is:

```text
active_memory.jsonl
```

This file stores only structured observations derived from each run's `REFCHECKER_REPAIR_LOG`.

Do not write the following into `active_memory.jsonl`:

- full reports
- full paper text
- hidden chain-of-thought or temporary reasoning
- human annotation
- broad self-reflection not grounded in `REFCHECKER_REPAIR_LOG`
- OpenClaw session history

The purpose is to test whether prior refchecker/repair experiences help later report generation and repair, not whether arbitrary accumulated context helps.

## Memory Data Model

Each `REFCHECKER_REPAIR_LOG` row becomes at most one memory record.

Minimum schema:

```json
{
  "condition": "memory_on",
  "pass_id": "P1",
  "case_id": "C1",
  "source_run_id": "P1_C1",
  "item_type": "claim_citation_pair",
  "citation_tag": "B",
  "issue_type": "overclaim",
  "issue_summary": "...",
  "repair_action": "weaken_claim",
  "topic": "...",
  "summary_en": "...",
  "keywords": []
}
```

Allowed `item_type` values:

```text
reference_metadata
claim_citation_pair
```

Allowed `issue_type` values should follow the refchecker repair prompt:

```text
none
metadata_error
support_error
overclaim
scope_error
uncertain
```

For retrieval injection, non-`none` rows should be ranked before clean rows. Clean rows may be kept for auditability, but they should not dominate the prompt context.

## Memory Flow

Each `memory_on` case follows this loop:

```text
1. Build query from current case topic and task intent.
2. Retrieve top-k records from active_memory.jsonl.
3. Inject a compact MEMORY_CONTEXT section into the prompt.
4. Run the same report -> refchecker -> repair task.
5. Extract REFCHECKER_REPAIR_LOG from output.raw.txt.
6. Append normalized memory records to active_memory.jsonl.
7. Log retrieval results to retrieve_log.jsonl.
```

The injected context must be framed as procedural caution only:

```text
MEMORY_CONTEXT may warn about prior citation or repair errors.
It is not evidence. Do not cite it. All scientific claims must still be
supported by [A]-[F] source materials.
```

## Isolation Rules

`M0`:

- one profile per output
- one workspace per output
- no memory read
- no memory write

`M1`:

- one shared experiment workspace or one shared memory directory
- one new session key per case/pass
- one shared `active_memory.jsonl`
- one shared `retrieve_log.jsonl`
- no direct reuse of prior report text except through retrieved memory summaries

The current case PDFs should be made available in a predictable case-local path. Any arxiv cache sharing should be treated carefully: if cache sharing is enabled for stability, it must be recorded as a fixed infrastructure choice, not as a memory mechanism.

## Relationship to Existing scripts/

The existing `scripts/` action-memory draft is more fine-grained than needed for the formal MVP. It records and retrieves around individual actions such as `fetch_paper`, `search_papers`, and `make_claim`.

For the MVP, reuse only the simple parts:

- JSONL append behavior
- BM25-style retrieval logic
- retrieval logging

Do not use the full action-by-action loop in the formal experiment. It would introduce extra intervention points and make the memory effect harder to attribute.

Required implementation should instead provide small dedicated scripts for:

```text
prepare_main_memory_runs.sh
setup_main_memory_profiles.sh
retrieve_memory_context.py
extract_refchecker_memory.py
run_main_memory_runs.sh
collect_main_memory_outputs.sh
```

## Success Criteria

Before full execution, a smoke test must show:

- `M0` still runs with memory disabled.
- `M1 P1 C1` runs with empty or near-empty memory context.
- `M1 P1 C2` receives memory records written from `P1 C1`.
- `active_memory.jsonl` contains only normalized `REFCHECKER_REPAIR_LOG` derived rows.
- `retrieve_log.jsonl` records the query, selected memory rows, and injected context.
- The final output still contains:
  - `# ORIGINAL_REPORT`
  - `# REFCHECKER_REPAIR_LOG`
  - `# REPAIRED_REPORT`
  - `# RUN_SUMMARY`

## Known Limitations

The case order is fixed rather than counterbalanced. This makes the run easier to reproduce but means memory effects can be confounded with case order and case difficulty. The analysis should therefore report both:

- within-pass trend across C1 -> C5
- same-case trend across P1 -> P2 -> P3

The memory intervention is a combined retrieval-plus-injection condition. If `M1` improves over `M0`, this design supports the usefulness of the MVP memory package, not a separate attribution to active retrieval versus passive memory exposure.
