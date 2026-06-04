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
你是一名科研助理。你需要完成一份科研报告，并在报告生成后使用 refchecker 对学术引用进行核查和修复。

本任务分为三个阶段。三个阶段必须在同一次最终回复中按顺序输出。

---

## 阶段 1：生成未修复初稿 ORIGINAL_REPORT

你需要基于给定课题和论文材料撰写一份结构化研究笔记。

### 阶段 1 硬性规则

- 这一阶段不得调用 refchecker / verify_citation。
- 这一阶段生成的初稿视为 frozen original。进入阶段 2 后，不得回头改写 ORIGINAL_REPORT。
- 你必须阅读 workspace 中提供的 [A]、[B]、[C] 三篇 PDF。
- 你必须自行检索并获取三篇高度相关的开放获取论文，标记为 [D]、[E]、[F]。
- 最终报告只能引用 [A]~[F] 六篇论文。
- 第二部分每条结论必须有 [A]~[F] 出处标签和 CPS 位置标注。

### 课题

多模态大模型（MLLM，如 GPT-4V、Gemini）是否具备了类似人类的视觉理解能力？

### 提供的论文 PDF

PDF 文件位于当前 profile workspace 的：

```text
input_papers/case4/MMPerspective.pdf
input_papers/case4/What's in Common_Multimodal Models Hallucinate When Reasoning Across Scenes.pdf
input_papers/case4/HumanCognitive Benchmarks Reveal Foundational.pdf
```

提供论文元信息：

[A] Tang et al. (2025). "MMPerspective: Do MLLMs Understand Perspective? A Comprehensive Benchmark for Perspective Perception, Reasoning, and Robustness." arXiv:2505.20426.
[B] Ross et al. (2025). "What's in Common? Multimodal Models Hallucinate When Reasoning Across Scenes." arXiv:2511.03768.
[C] Huang et al. (2025). "VisFactor: Benchmarking Fundamental Visual Cognition in Multimodal Large Language Models." arXiv:2502.16435.

### 自主检索要求

- 优先使用 arXiv 或其他开放获取平台。
- 优先选择 2024-2025 年论文。
- 选择与课题直接相关的论文，不要选择只主题沾边的论文。
- 在第三部分列出 [D]~[F] 的完整信息和检索策略。

### ORIGINAL_REPORT 格式

ORIGINAL_REPORT 必须包含以下三个部分，总计约 800 中文字：

#### 第一部分：总体评估

基于全部六篇论文，概括当前证据状况、共识/分歧、局限或 gap。

#### 第二部分：逐条结论

提取 5-8 条具体、可被证伪的结论。每条使用：

```text
- 结论陈述。
  出处：[A] §N.M::¶K / [B] §N.M::TK
```

所有引用位置必须遵守 citation-standard 的 CPS 格式。

#### 第三部分：引用论文清单

列出 [A]~[F] 六篇论文的完整元信息：

```text
- [Tag] 作者 (年份). "标题." 发表刊物/预印本平台. 标识符. 检索词: {检索策略}
```

对于 [A]~[C]，检索词填写 `provided_pdf`。

---

## 阶段 2：REFCHECKER_REPAIR_LOG

你必须对 ORIGINAL_REPORT 中的 [A]~[F] 引用清单和关键 claim-citation pair 做核查。

### 必须使用的工具

- 对 [A]~[F] 六篇引用条目逐条调用 refchecker 的 `verify_citation`。
- 调用时尽量提供 title、authors、year、doi、arxiv_id、url。
- 如果某篇论文缺少 DOI 或 arXiv ID，也要用 title/year/authors 调用。

### 核查边界

- refchecker 结果只判断引用元数据真实性和匹配度。
- 你还必须基于已阅读的 PDF/全文检查 claim 是否被引用位置支持。
- 如果 refchecker 未能确认某条引用，不要编造；在 repair log 中写 `uncertain`。

### REFCHECKER_REPAIR_LOG 格式

只输出 JSONL 代码块。每行一个 JSON 对象：

```jsonl
{"case_id":"C4","run_id":"P2_C4","item_id":"ref_A","item_type":"reference_metadata","citation_tag":"A","tool_called_refchecker":"yes","refchecker_verified":"yes_or_no_or_uncertain","issue_type":"none_or_metadata_error_or_support_error_or_overclaim_or_scope_error_or_uncertain","issue_summary":"一句话说明问题","repair_action":"none_or_correct_metadata_or_remove_claim_or_weaken_claim_or_replace_citation_or_mark_uncertain"}
{"case_id":"C4","run_id":"P2_C4","item_id":"claim_01","item_type":"claim_citation_pair","citation_tag":"A","tool_called_refchecker":"yes_or_no","refchecker_verified":"yes_or_no_or_uncertain","issue_type":"none_or_metadata_error_or_support_error_or_overclaim_or_scope_error_or_uncertain","issue_summary":"一句话说明 claim 与引用的关系","repair_action":"none_or_correct_metadata_or_remove_claim_or_weaken_claim_or_replace_citation_or_mark_uncertain"}
```

至少包含：

- 6 行 reference metadata 检查记录：`ref_A` 到 `ref_F`。
- 每条第二部分结论至少 1 行 claim-citation pair 检查记录。

---

## 阶段 3：生成修复后报告 REPAIRED_REPORT

基于 REFCHECKER_REPAIR_LOG 修复 ORIGINAL_REPORT。

### 修复规则

- 如果引用元数据错误，修正第三部分引用清单。
- 如果 claim 超出引用材料支持范围，弱化 claim。
- 如果引用不能支持 claim，替换为能支持的 [A]~[F] 引用；如果没有可替代引用，删除该 claim。
- 不要新增未经检查的强 claim。
- REPAIRED_REPORT 仍必须只引用 [A]~[F] 六篇论文。
- REPAIRED_REPORT 仍必须遵守 CPS 引用位置格式。

---

## 最终输出格式

最终回复必须严格按以下四个顶层标题输出：

# ORIGINAL_REPORT

{阶段 1 初稿}

# REFCHECKER_REPAIR_LOG

```jsonl
{阶段 2 JSONL}
```

# REPAIRED_REPORT

{阶段 3 修复后报告}

# RUN_SUMMARY

```json
{"case_id":"C4","run_id":"P2_C4","tool_called_refchecker":"yes_or_no","num_references_checked":0,"num_claim_pairs_checked":0,"num_issues_found":0,"num_revisions_made":0}
```

除上述四个顶层标题外，不要输出额外解释。
