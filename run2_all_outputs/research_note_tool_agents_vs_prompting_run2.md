# Research Note: Tool-Augmented LLM Agents vs Pure LLM Prompting
## Run 2 — 2026-06-08 | 金咪 🐱
### Case: exp_tool_agents_vs_prompting_run2
### Objective: Verify / Challenge / Extend Run 1 conclusions with 3 new papers

---

## Papers Selected (beyond [S1]-[S9])

| Tag | Paper | arXiv ID | Year | Why Selected |
|-----|-------|----------|------|-------------|
| [S10] | **Kimi-Dev**: Agentless Training as Skill Prior for SWE-Agents | 2509.23045 | 2025 | Directly addresses the Agentless-vs-Agent binary from Run 1 Claim 3 |
| [S11] | **AgentLens**: Revealing The Lucky Pass Problem in SWE-Agent Evaluation | 2605.12925 | 2026 | Challenges the pass@1 metric used throughout Run 1 Claims 1-2 |
| [S12] | **Live-SWE-agent**: Can SE Agents Self-Evolve on the Fly? | 2511.13646 | 2025 | Extends self-improvement (Run 1 Claim 8) to online runtime evolution |

---

## Claims Extracted (5 new claims, #14-#18)

### Claim 14 [S10, Abstract] (E)
- **Kimi-Dev**: Agentless training (single-turn verifiable steps: localization, code edit, self-reflection) induces structured skill priors transferable to SWE-Agent frameworks.
- Achieves **60.4% on SWE-bench Verified** as workflow (best among Agentless methods).
- After SFT adaptation on 5k trajectories: **48.6% pass@1** as SWE-agent, on par with Claude 3.5 Sonnet.
- **Challenges Run 1 Claim 3**: The "Agentless paradox" (simple pipeline > complex agents) is not a binary opposition — Agentless training provides transferable skill priors.
- **Validation status**: SUPPORTS Run 1 Claim 3 (Agentless efficacy) but REFRAMES it as complementarity rather than contradiction.

### Claim 15 [S11, Abstract] (E)
- **AgentLens**: 10.7% of passing SWE-bench trajectories are "Lucky Passes" — solutions that pass tests via regression cycles, blind retries, missing verification, or disordered exploration.
- Evaluated 2,614 OpenHands trajectories from 8 model backends on 60 SWE-bench Verified tasks.
- Lucky Pass rates: 0.5% to 23.2% depending on model.
- Quality-adjusted ranking shifts models by up to 5 rank positions.
- **Challenges Run 1 Claims 1-2**: The binary pass/fail metric central to all Run 1 benchmark comparisons is contaminated by ~10.7% false positives. The actual agent advantage may be smaller than reported.
- **Validation status**: UNDERMINES precision of Run 1 benchmark claims (Claims 1-2, 5).

### Claim 16 [S12, Abstract] (E)
- **Live-SWE-agent**: First live software agent to autonomously evolve its own scaffold at runtime.
- Starts from minimal scaffold (mini-SWE-agent with bash tools only), evolves scaffold while solving.
- Achieves **77.4% on SWE-bench Verified** without test-time scaling — outperforms all existing agents including proprietary.
- On **SWE-Bench Pro**: 45.8% (best-known).
- **Extends Run 1 Claim 8** (SICA 17%→53% offline self-improvement) to online runtime evolution.
- **Contradicts Run 1 Claim 6**: The ablation showing file navigation as the single largest contributor (−47%) becomes less relevant if scaffold can be auto-evolved rather than manually optimized.
- **Validation status**: CONFIRMS and EXTENDS the self-improvement paradigm. PARTIALLY SUPERSEDES manual scaffold design analysis.

### Claim 17 [S10+S11+S12, Meta-analysis] (I)
- **Meta-finding**: Run 2's three papers collectively dissolve the "tool-augmented vs pure prompting" binary from Run 1:
  1. [S10] Agentless and Agent are complementary (skill priors benefit both).
  2. [S11] The pass@1 metric has significant noise (~10.7% Lucky Pass contamination).
  3. [S12] Scaffold design can be automated via runtime evolution, reducing the importance of manual ACI design.
- The relevant comparison dimension shifts to: **"skill-structured training + runtime adaptation"** vs static prompting.
- **Validation status**: REFRAMES Run 1's core comparative framing.

### Claim 18 [S1+S2+S10+S12, Meta-analysis] (E/I)
- **Explosive SWE-bench progress**: SWE-agent 12.5% (2024) → Kimi-Dev 60.4% (2025) → Live-SWE-agent 77.4% (2025) = ~6.2× improvement in ~18 months.
- Raises question: Does the 1.7% GPT-4 zero-shot baseline [S2] still represent a meaningful comparison point?
- The rapid agent improvement trajectory suggests the comparative framework from Run 1 may have a short half-life.
- **Validation status**: OBSERVES trend; Run 1's framework may need temporal calibration.

---

## Verification Status: 5 New Claims

| Claim | Source | Verification | Numerics Verified? | Citation Correct? | Overclaim? |
|-------|--------|-------------|-------------------|-------------------|------------|
| #14 | [S10] Abstract | ✅ web_fetch | 60.4%, 48.6% in Abstract | ✅ [S10] | No — numbers in Abstract |
| #15 | [S11] Abstract | ✅ web_fetch | 10.7%, 0.5-23.2%, 5 ranks in Abstract | ✅ [S11] | No — numbers in Abstract |
| #16 | [S12] Abstract | ✅ web_fetch | 77.4%, 45.8% in Abstract | ✅ [S12] | No — numbers in Abstract |
| #17 | Meta (S10+S11+S12) | I (interpretive) | N/A | ✅ Tags correct | No — interpretive synthesis |
| #18 | Meta (S1+S2+S10+S12) | E/I | 12.5%→60.4%→77.4% | ✅ Tags correct | No — cited sources verified |

Note: Run 1 had 2 mis-citations corrected in audit:
- Claim 1: GPT-4 1.7% attributed to [S1, Abstract] but not in SWE-agent Abstract → actually from [S2, Abstract]
- Run 2 avoids this by citing [S2] for the 1.7% baseline

---

## Run 1 vs Run 2: Cross-Validation Matrix

| Run 1 Claim | Run 2 Finding | Verdict |
|-------------|--------------|---------|
| **C1**: 7.4× SWE-bench gain | AgentLens shows ~10.7% of passes are Lucky | **WEAKENED** — metric contaminated |
| **C2**: 1.2× HumanEvalFix gain | Not re-examined | **UNCHANGED** (no new data) |
| **C3**: Agentless paradox | Kimi-Dev reframes as complementarity | **REFINED** — not binary opposition |
| **C4**: CodeAct 20% gain | Not re-examined | **UNCHANGED** |
| **C5**: Task type drives magnitude | AgentLens undermines pass metric | **PARTIALLY WEAKENED** |
| **C6**: File navigation −47% | Live-SWE-agent auto-evolves scaffold | **SUPERSEDED** — auto-scaffold |
| **C7**: Complexity threshold | Not re-examined | **UNCHANGED** |
| **C8**: SICA 17%→53% | Live-SWE-agent 77.4% online evolution | **EXTENDED** — offline→online |
| **C9**: CodeNav ≤2pp F1 | Not re-examined | **UNCHANGED** |
| **C10**: ToolMaker 80% | Not re-examined | **UNCHANGED** |
| **C11**: Voyager skill composition | Not re-examined | **UNCHANGED** |
| **C12**: Four code empowerment mechanisms | Not re-examined | **UNCHANGED** |
| **C13**: Costs 10-50× | Not re-examined | **UNCHANGED** |

**Summary**: Of 13 Run 1 claims, 2 weakened, 1 refined, 1 partially weakened, 1 superseded, 1 extended, 7 unchanged.

---

## Key Divergences / Contradictions

1. **Metric contamination**: AgentLens is the first systematic analysis showing SWE-bench pass@1 has a systematic false positive rate (~10.7%). This affects the quantitative foundation of Run 1.
2. **From binary to spectrum**: Kimi-Dev dissolves the "Agentless vs Agent" framing into a "skill prior + fine-tuning" spectrum.
3. **Scaffold design obsolescence**: Live-SWE-agent's runtime evolution suggests hand-crafted ACIs (SWE-agent's core contribution) may be an intermediate step rather than the end state.
4. **Rapid progress rate**: 77.4% in 2025 vs 12.5% in 2024 means Run 1's numbers may have a short validity window.

---

## Methodological Notes

- All new papers verified via arXiv web_fetch (abstracts only).
- Claims 17-18 are interpretive meta-claims labeled [I] (interpretive) or [E/I] (evidence + interpretation).
- No full paper review; claims are Abstract-grounded.
- Action memory: 9 steps recorded + pre_action_hook for each make_claim.
- Cross-case retrieval in pre_action_hook successfully surfaced Run 1 claims for context.
