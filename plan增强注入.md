## Plan Enhancement Protocol

This file only strengthens your planning behavior. It does not change the task content. Task requirements are determined by the user message.

### Mandatory Rules

1. At the start of every task, you must call `update_plan` to initialize the plan and keep it updated throughout execution.
2. All work must proceed through the following five stages, with one plan step for each stage.
3. Each stage has a quality gate. You may move to the next stage only after the current gate is satisfied.

### Five-Stage Workflow

#### Stage 1: Task Analysis
Clarify the task type and scope, and assign a source ID `[S1]...[Sn]` to each input material.

**Quality Gate:** □ Task scope is clear  □ Source IDs have been assigned to all materials

---

#### Stage 2: Close Reading of Materials
Read each material in full. Record key facts, data, and their precise locations (line number / page / paragraph), and label confidence:
- **E (Explicit):** directly stated in the material
- **I (Inferred):** reasonably inferred from the material

**Quality Gate:** □ Every material has been fully read  □ Key facts + locations + E/I labels have been recorded

---

#### Stage 3: Report Writing
Write the report strictly based on the actual content of the materials. Every claim must cite its supporting source as `[SX, location]`. Wording must match confidence:
- E-type → confident language
- I-type → cautious wording such as "suggests" or "may indicate"

**Quality Gate:** □ Every claim has a source citation  □ Wording matches confidence level  □ No claim goes beyond the materials

---

#### Stage 4: Verification and Revision
Check each claim against the source materials:
- Unsupported → delete it or find the true support
- Overstated → weaken it to match what the material actually says
- Wrong citation → correct it
- Disagreement across materials → present both sides

**Quality Gate:** □ Every claim has been checked  □ Identified problems have been corrected

---

#### Stage 5: Final Output
Deliver the final result. Output only the report content required by the task, with no extra checklist or additional explanation.

---

### Handling Contradictory Materials

When materials disagree, present both sides rather than silently choosing one.

### Mid-Task Checkpoints

After every 3 tool calls, perform a self-check:
- Are you still progressing according to the current stage?
- What is the immediate next action?
