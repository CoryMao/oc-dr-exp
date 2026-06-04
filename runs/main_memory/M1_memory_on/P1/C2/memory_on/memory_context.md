## OUTPUT_CONTRACT_REMINDER

Your final response must include exactly these four top-level headings in this order:
# ORIGINAL_REPORT
# REFCHECKER_REPAIR_LOG
# REPAIRED_REPORT
# RUN_SUMMARY
Do not omit # ORIGINAL_REPORT. Do not output any prelude or explanation before the required report sections.

## MEMORY_CONTEXT

These prior records are procedural cautions only. Do not cite them. They are not scientific evidence.
All scientific claims must still be supported by [A]-[F] source materials and CPS locations.

Retrieved top 6 prior refchecker repair records:
- M1: source=P1_C1 case=C1 item=claim_06 tag=A issue=overclaim action=weaken_claim; claim_06 [A] [A] primarily evaluates on SWE-Bench Verified, LiveCodeBench and synthetic benchmarks. The paper does not specifically report agent scaffolding degradation on reasoning-heavy tasks (AIME/GPQA). This claim...
- M2: source=P1_C1 case=C1 item=claim_01 tag=A issue=overclaim action=weaken_claim; claim_01 [A] Claim states agent performance exceeds prompting by 'an order of magnitude'. [E] T1 shows SWE-agent 18.00% vs RAG 2.67% on Lite (~6.7×), and 12.47% vs 1.31% on full (~9.5×), close but not strictly an orde...
- M3: source=P1_C1 case=C1 item=ref_D tag=D issue=metadata_error action=correct_metadata; ref_D [D] Year mismatch: cited 2025 but actual arXiv year is 2024 (published at ICLR 2025). Venue is ICLR 2025, not just arXiv preprint. Repair action: correct_metadata.
- M4: source=P1_C1 case=C1 item=claim_02 tag=A issue=none action=none; claim_02 [A] 17%→53% improvement directly from [A] Abstract and §4 results. Data consistent with citation.
- M5: source=P1_C1 case=C1 item=ref_B tag=B issue=metadata_error action=correct_metadata; ref_B [B] Author mismatch: cited 'Gao, Tian et al.' but actual authors are 'Trae Research Team, Pengfei Gao, Zhao Tian, Xiangxin Meng, Xinchen Wang, Ruida Hu, Yuanan Xiao, Yizhou Liu, Zhao Zhang, Junjie Chen, Cuiyun G...
- M6: source=P1_C1 case=C1 item=claim_03 tag=B issue=none action=none; claim_03 [B] Ensemble reasoning three components (generation, pruning, selection) from [B] §3.1; performance data from §5.

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
