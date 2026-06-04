## Memory Writeback
In each task round, the main agent must not only complete the current task but also perform controlled memory writeback. See:

- `MEMORY_WRITEBACK_RULES.md`

Execution requirements:

1. At the end of each round, first produce the formal output, then generate the feedback card, and only then update memory.
2. You must update `memory/YYYY-MM-DD.md` before deciding whether to update `MEMORY.md`.
3. Only stable, reusable, and confirmed information may be written into `MEMORY.md`.
4. Do not write full outputs, unverified guesses, temporary reasoning, or one-off details into `MEMORY.md`.
5. If you are unsure whether a piece of information should enter long-term memory, do not write it.
