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
- M4: source=P1_C1 case=C1 item=ref_B tag=B issue=metadata_error action=correct_metadata; ref_B [B] Author mismatch: cited 'Gao, Tian et al.' but actual authors are 'Trae Research Team, Pengfei Gao, Zhao Tian, Xiangxin Meng, Xinchen Wang, Ruida Hu, Yuanan Xiao, Yizhou Liu, Zhao Zhang, Junjie Chen, Cuiyun G...
- M5: source=P1_C2 case=C2 item=ref_A tag=A issue=metadata_error action=correct_metadata; ref_A [A] 第一作者错误：引用为 Huang et al.，实际作者为 Figarri Keisha, Zekun Wu, Ze Wang, Adriano Koshiyama, Philip Treleaven，不存在 Huang 这位作者 Repair action: correct_metadata.
- M6: source=P1_C1 case=C1 item=claim_08 tag=C issue=none action=none; claim_08 [C] 80% task completion rate from [C] §4 Benchmark evaluation results.

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
