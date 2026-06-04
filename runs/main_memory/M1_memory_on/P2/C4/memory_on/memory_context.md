## OUTPUT_CONTRACT_REMINDER

Your final response must include exactly these four top-level headings in this order:
# ORIGINAL_REPORT
# REFCHECKER_REPAIR_LOG
# REPAIRED_REPORT
# RUN_SUMMARY
Do not omit # ORIGINAL_REPORT. Do not output any prelude or explanation before the required report sections.
If you need scratch files, write them under `.openclaw/tmp/` inside the workspace; never use `/tmp` or paths outside the workspace.

## MEMORY_CONTEXT

These prior records are procedural cautions only. Do not cite them. They are not scientific evidence.
All scientific claims must still be supported by [A]-[F] source materials and CPS locations.

Retrieved top 6 prior refchecker repair records:
- M1: source=P1_C5 case=C5 item=ref_C tag=C issue=metadata_error action=correct_metadata; ref_C [C] Author name mismatch: 'Beth Barnes' should be 'Elizabeth Barnes' in actual paper metadata Repair action: correct_metadata.
- M2: source=P3_C5 case=C5 item=ref_F tag=F issue=metadata_error action=correct_metadata; ref_F [F] 年份和发表刊物均需修正：Semantic Scholar记录论文年份为2024（arXiv预印本2024年12月）；发表刊物应更准确地注明为'CHI EA '25 (Extended Abstracts of the CHI Conference on Human Factors in Computing Systems, ACM)'而非简写'CHI EA '25 (ACM)' Repair action: c...
- M3: source=P1_C5 case=C5 item=claim_07 tag=F issue=scope_error action=weaken_claim; claim_07 [F] Claim cites §5::¶2 and §8::¶2 for contradictory code quality evidence and lack of longitudinal studies; these references are broadly correct but §8 is Discussion/Implications, not a section with numbered...
- M4: source=P2_C3 case=C3 item=claim_06 tag=C issue=scope_error action=weaken_claim; claim_06 [C] claim 声称 '面对新颖结合口袋时失败率超过 50%'，[C] §3.2::¶1 明确指 AF3 在 DockGen-E 数据集（n=122）上失败率 >50%，但该数据集有特定来源（PDB 2019 后沉积 + ECOD 功能域过滤），不能泛化为所有新颖结合口袋 Repair action: weaken_claim.
- M5: source=P3_C5 case=C5 item=claim_07 tag=F issue=scope_error action=weaken_claim; claim_07 [F] [F] §4.3::¶末包含开发者将WCA比作'intern'/'junior developer'的引述，支持claim前半部分；但[C] §3.3::¶1讨论的是因素分析（factor analysis）方法论框架（21个因素四分类），并非开发者对AI能力层级的评价，无法支持'跨多项研究'的跨研究拓展 Repair action: weaken_claim.
- M6: source=P1_C3 case=C3 item=claim_06 tag=D issue=scope_error action=weaken_claim; claim_06 [D] [D] Table II 和 §III-C 报告 IPBind Pearson R=0.732 at LBA30，19.6% 相对提升无误；但 claim 未提及这是在特定 Atom3D benchmark split 上的结果 Repair action: weaken_claim.

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
