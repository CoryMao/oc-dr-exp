# arxiv MCP 预实验 Prompt

目的：测试 `arxiv MCP` 是否能帮助 Agent 自主选择更合适的 [D]、[E]、[F] 三篇论文。

运行说明：

- 每个 case 在 `arxiv_off` 和 `arxiv_on` 两个条件下各运行 3 次：`R1`、`R2`、`R3`。
- 本预实验只要求选择 [D]、[E]、[F]，不要求生成完整研究报告。
- 工具开关由 OpenClaw/workspace 配置控制，不依赖 prompt 约束。
- Agent 输出填入 `evaluation/pre_experiments/arxiv_mcp_records.csv`。
- 以下字段由人工标注，Agent 必须留空：`topic_relevance`、`is_duplicate`、`is_tangential`、`valid_paper`、`selection_note`。

## Template: arxiv_off

```text
你是一名科研助理。你的任务不是撰写完整研究报告，而是为后续报告任务补充三篇候选论文。

你需要基于给定课题和已提供的三篇论文 [A]、[B]、[C]，选择三篇额外论文，分别标记为 [D]、[E]、[F]。

## 硬性规则

- 不要撰写研究报告。
- 只基于下面给定的课题和三篇已提供论文信息选择候选论文。
- 不要写入 memory。
- 不要调用 write、edit、exec、process 等文件或命令工具；只在最终回复中输出 3 行 CSV。
- 不要选择与 [A]、[B]、[C] 重复或高度重复的论文。
- 不要选择只和课题“擦边相关”的论文。
- 优先选择与 citation faithfulness、scientific claim verification、evidence attribution、hallucinated citations 或 citation-conclusion mismatch 直接相关的论文。
- 如果你无法确认某篇论文的题名、年份或标识符，不要捏造；对应字段填写 `unknown`。

---

## 课题

{topic}

---

## 已提供论文

[A] {paper_a_title}
Identifier: {paper_a_id_or_url}

[B] {paper_b_title}
Identifier: {paper_b_id_or_url}

[C] {paper_c_title}
Identifier: {paper_c_id_or_url}

---

## 输出要求

只输出 3 行 CSV，不要输出表头，不要添加解释。

每行对应一篇候选论文，分别为 [D]、[E]、[F]。

CSV 字段顺序必须严格如下：

case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note

字段填写规则：

- `case_id` 固定填写：{case_id}
- `run_id` 固定填写：{run_id}
- `condition` 固定填写：arxiv_off
- `selected_tag` 只能填写：D / E / F
- `full_text_available` 如果无法确认，填写 `unknown`
- `topic_relevance` 留空
- `is_duplicate` 留空
- `is_tangential` 留空
- `valid_paper` 留空
- `selection_note` 留空

示例格式：

{case_id},{run_id},arxiv_off,D,"paper title","paper id or url",2024,unknown,,,,,
```

## Template: arxiv_on

```text
你是一名科研助理。你的任务不是撰写完整研究报告，而是为后续报告任务补充三篇候选论文。

你需要基于给定课题和已提供的三篇论文 [A]、[B]、[C]，使用 arxiv MCP 自主检索并选择三篇额外论文，分别标记为 [D]、[E]、[F]。

## 硬性规则

- 不要撰写研究报告。
- 自主检索并确认候选论文的元信息。
- 不要写入 memory。
- 不要调用 write、edit、exec、process 等文件或命令工具；只在最终回复中输出 3 行 CSV。
- 不要选择与 [A]、[B]、[C] 重复或高度重复的论文。
- 不要选择只和课题“擦边相关”的论文。
- 优先选择 arXiv 或其他可开放获取全文的论文。
- 优先选择 2024-2025 年的论文；如果更早论文明显更相关，也可以选择，但需要在标识符和年份字段中如实填写。
- 优先选择与 citation faithfulness、scientific claim verification、evidence attribution、hallucinated citations 或 citation-conclusion mismatch 直接相关的论文。
- 如果检索结果无法确认题名、年份或标识符，不要捏造；对应字段填写 `unknown`。

---

## 课题

{topic}

---

## 已提供论文

[A] {paper_a_title}
Identifier: {paper_a_id_or_url}

[B] {paper_b_title}
Identifier: {paper_b_id_or_url}

[C] {paper_c_title}
Identifier: {paper_c_id_or_url}

---

## 输出要求

只输出 3 行 CSV，不要输出表头，不要添加解释。

每行对应一篇候选论文，分别为 [D]、[E]、[F]。

CSV 字段顺序必须严格如下：

case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note

字段填写规则：

- `case_id` 固定填写：{case_id}
- `run_id` 固定填写：{run_id}
- `condition` 固定填写：arxiv_on
- `selected_tag` 只能填写：D / E / F
- `full_text_available` 根据 arxiv MCP 检索结果填写 `yes` / `no` / `unknown`
- `topic_relevance` 留空
- `is_duplicate` 留空
- `is_tangential` 留空
- `valid_paper` 留空
- `selection_note` 留空

示例格式：

{case_id},{run_id},arxiv_on,D,"paper title","arXiv:2501.12345",2025,yes,,,,,
```
