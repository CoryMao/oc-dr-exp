# OpenClaw Citation-Conclusion Inconsistency Experiment Design

## 1. Experiment Architecture

The experiment is organized into two layers. Layer 1 validates the usefulness of the MCP tools as intermediate capabilities. Layer 2 fixes the validated tool stack and evaluates the main scaffold variables: planning and memory.

### 1.1 Layer 1: Tool Effectiveness Pre-Experiments

The purpose of Layer 1 is to show that `arxiv MCP` and `mcp-refchecker` affect relevant intermediate abilities before they are fixed in the main experiment.

#### arxiv MCP Pre-Experiment

Goal: test whether the agent can autonomously select appropriate [D], [E], and [F] papers.

- Comparison: without `arxiv MCP` vs with `arxiv MCP`
- Input: the topic and provided papers [A], [B], and [C] for each of the five cases
- Output: the three autonomously selected papers [D], [E], and [F]
- Evaluation criteria:
  - Topic relevance
  - Full-text availability
  - No duplicate or near-duplicate papers
  - Not merely tangential to the topic
  - Preference for 2024-2025 papers where appropriate
  - Ability to provide evidence for the target topic

#### mcp-refchecker Pre-Experiment

Goal: test whether `mcp-refchecker` helps detect claim-citation problems.

- Comparison: self-checking without `mcp-refchecker` vs self-checking with `mcp-refchecker`
- Input: the same agent reports and source PDFs
- Output: claim-level verification results
- Evaluation criteria:
  - Ability to identify unsupported claims
  - Ability to identify overclaims
  - Ability to identify mis-citations
  - Ability to identify contradictions
  - Detection rate relative to human annotation

### 1.2 Layer 2: Main Experiment

The main experiment fixes the tool stack and varies only planning and memory.

Fixed setup:

```text
pdf skill = on
citation_standard skill = on
arxiv MCP = on
mcp-refchecker = on
model = Deepseek v4 Pro
framework = OpenClaw + selected skills + MCP + memory setting
case order = 1 -> 2 -> 3 -> 4 -> 5
```

The `citation_standard` skill is fixed across all main-experiment conditions. It standardizes citation position syntax so that reports are easier to audit and can be checked by script. It is not treated as a main experimental variable, and CPS formatting failures are reported separately from citation-conclusion inconsistency errors.

Main variables:

```text
Plan = no plan / default plan / AGENTS.md guided plan
Memory = no memory / passive memory / active memory
```

Run count:

```text
No Memory:
5 cases x 3 plan conditions x 2 runs = 30 outputs

Passive Memory:
5 cases x 3 plan conditions x 3 passes = 45 outputs

Active Memory:
5 cases x 3 plan conditions x 3 passes = 45 outputs

Total main experiment = 120 outputs
```

Memory conditions use a shared-memory sequential design:

```text
pass1: Case1 -> Case2 -> Case3 -> Case4 -> Case5
pass2: Case1 -> Case2 -> Case3 -> Case4 -> Case5
pass3: Case1 -> Case2 -> Case3 -> Case4 -> Case5
```

Each memory-enabled round follows this sequence:

```text
formal report
-> verification/self-audit prompt
-> feedback card
-> daily memory writeback
-> conditional long-term MEMORY.md writeback
```

The `No Memory` condition generates only the formal report and logs. It does not read or write memory. Independent self-audit or refchecker evaluation may still be run for analysis, but its result must not be fed back into the agent.

### 1.3 Known Design Limitation

All conditions use the fixed case order `1 -> 2 -> 3 -> 4 -> 5`. This improves reproducibility and log readability, but it does not counterbalance case order. Therefore, observed improvements in memory-enabled conditions may be partly affected by case difficulty order. To reduce this risk, the analysis will report both:

- within-pass trend: whether error rates change from Case1 to Case5 within the same pass
- same-case across-pass trend: whether the same case improves from pass1 to pass2 to pass3
