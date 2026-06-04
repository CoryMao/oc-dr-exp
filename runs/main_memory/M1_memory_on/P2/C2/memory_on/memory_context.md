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
- M1: source=P1_C2 case=C2 item=ref_A tag=A issue=metadata_error action=correct_metadata; ref_A [A] 第一作者错误：引用为 Huang et al.，实际作者为 Figarri Keisha, Zekun Wu, Ze Wang, Adriano Koshiyama, Philip Treleaven，不存在 Huang 这位作者 Repair action: correct_metadata.
- M2: source=P1_C2 case=C2 item=claim_03 tag=F issue=none action=none; claim_03 [F] [F] §1.1 Result #1 明确声明即使 1% 合成数据也可导致 strong model collapse，破坏 scaling law；§3.1 给出理论证明，claim 被充分支持
- M3: source=P1_C2 case=C2 item=claim_02 tag=E issue=none action=none; claim_02 [E] [E] §2 在 transformers/diffusion/VAE 三类模型上实证数据累积避免 collapse；§3 提供线性模型理论证明，claim 被充分支持
- M4: source=P1_C2 case=C2 item=ref_E tag=E issue=none action=none; ref_E [E] 元数据与 arXiv:2404.01413 及 NeurIPS 2024 完全匹配，14 位作者、标题、年份均正确
- M5: source=P1_C2 case=C2 item=ref_C tag=C issue=none action=none; ref_C [C] 元数据与 arXiv:2505.08803 完全匹配：标题、作者（Zizhao Hu 等 3 人）、年份一致
- M6: source=P1_C2 case=C2 item=ref_F tag=F issue=none action=none; ref_F [F] 元数据与 arXiv:2410.04840 及 ICLR 2025 完全匹配，作者（Dohmatob 等 4 人）、标题、年份均正确

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
