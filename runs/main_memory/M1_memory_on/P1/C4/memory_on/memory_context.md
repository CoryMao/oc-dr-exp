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
- M1: source=P1_C3 case=C3 item=claim_06 tag=D issue=scope_error action=weaken_claim; claim_06 [D] [D] Table II 和 §III-C 报告 IPBind Pearson R=0.732 at LBA30，19.6% 相对提升无误；但 claim 未提及这是在特定 Atom3D benchmark split 上的结果 Repair action: weaken_claim.
- M2: source=P1_C3 case=C3 item=ref_D tag=D issue=metadata_error action=correct_metadata; ref_D [D] Refchecker 提示 venue 为 IEEE Open Journal of Engineering in Medicine and Biology，而非 arXiv preprint Repair action: correct_metadata.
- M3: source=P1_C1 case=C1 item=claim_06 tag=A issue=overclaim action=weaken_claim; claim_06 [A] [A] primarily evaluates on SWE-Bench Verified, LiveCodeBench and synthetic benchmarks. The paper does not specifically report agent scaffolding degradation on reasoning-heavy tasks (AIME/GPQA). This claim...
- M4: source=P1_C1 case=C1 item=claim_01 tag=A issue=overclaim action=weaken_claim; claim_01 [A] Claim states agent performance exceeds prompting by 'an order of magnitude'. [E] T1 shows SWE-agent 18.00% vs RAG 2.67% on Lite (~6.7×), and 12.47% vs 1.31% on full (~9.5×), close but not strictly an orde...
- M5: source=P1_C3 case=C3 item=ref_A tag=A issue=metadata_error action=correct_metadata; ref_A [A] Refchecker 提示 venue 缺失 bioRxiv 标识；论文实际发表于 Nature Machine Intelligence (2025)，ORIGINAL_REPORT 已包含该 venue 但未明确标注预印本服务器 bioRxiv Repair action: correct_metadata.
- M6: source=P1_C2 case=C2 item=ref_A tag=A issue=metadata_error action=correct_metadata; ref_A [A] 第一作者错误：引用为 Huang et al.，实际作者为 Figarri Keisha, Zekun Wu, Ze Wang, Adriano Koshiyama, Philip Treleaven，不存在 Huang 这位作者 Repair action: correct_metadata.

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
