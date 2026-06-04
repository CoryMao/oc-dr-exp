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
- M1: source=P3_C5 case=C5 item=claim_07 tag=F issue=scope_error action=weaken_claim; claim_07 [F] [F] §4.3::¶末包含开发者将WCA比作'intern'/'junior developer'的引述，支持claim前半部分；但[C] §3.3::¶1讨论的是因素分析（factor analysis）方法论框架（21个因素四分类），并非开发者对AI能力层级的评价，无法支持'跨多项研究'的跨研究拓展 Repair action: weaken_claim.
- M2: source=P1_C5 case=C5 item=ref_C tag=C issue=metadata_error action=correct_metadata; ref_C [C] Author name mismatch: 'Beth Barnes' should be 'Elizabeth Barnes' in actual paper metadata Repair action: correct_metadata.
- M3: source=P3_C5 case=C5 item=ref_C tag=C issue=metadata_error action=correct_metadata; ref_C [C] 作者名不精确：'Beth Barnes'实为'Elizabeth Barnes'，PDF元数据和refchecker均确认为Elizabeth Barnes Repair action: correct_metadata.
- M4: source=P1_C5 case=C5 item=claim_02 tag=B issue=overclaim action=weaken_claim; claim_02 [B] Claim asserts commercial/private codebase resolve rate '降至低水平' without specific number; paper's §5::T2 reports per-repo breakdown but exact commercial codebase figure needs explicit table reference Repair...
- M5: source=P1_C5 case=C5 item=claim_07 tag=F issue=scope_error action=weaken_claim; claim_07 [F] Claim cites §5::¶2 and §8::¶2 for contradictory code quality evidence and lack of longitudinal studies; these references are broadly correct but §8 is Discussion/Implications, not a section with numbered...
- M6: source=P1_C5 case=C5 item=ref_F tag=F issue=metadata_error action=correct_metadata; ref_F [F] Venue incorrectly listed as arXiv preprint only; actual publication venue is ACM Transactions on Software Engineering and Methodology (TOSEM) Repair action: correct_metadata.

Use these records only to avoid repeating citation metadata/support mistakes.

## TASK_PROMPT
