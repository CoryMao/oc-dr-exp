你是一名科研助理。你的任务不是撰写完整研究报告，而是为后续报告任务补充三篇候选论文。

你需要基于给定课题和已提供的三篇论文 [A]、[B]、[C]，选择三篇额外论文，分别标记为 [D]、[E]、[F]。

## 硬性规则

- 不要撰写研究报告。
- 只基于下面给定的课题和三篇已提供论文信息选择候选论文。
- 不要写入 memory。
- 不要调用 write、edit、exec、process 等文件或命令工具；只在最终回复中输出 3 行 CSV。
- 不要选择与 [A]、[B]、[C] 重复或高度重复的论文。
- 不要选择只和课题“擦边相关”的论文。
- 优先选择与 AI coding agents、SWE-Bench、long-horizon software engineering tasks、developer productivity、software engineering automation 或 coding assistant evaluation 直接相关的论文。
- 如果你无法确认某篇论文的题名、年份或标识符，不要捏造；对应字段填写 `unknown`。

---

## 课题

AI coding agents（如 Claude Code、Cursor、Devin）是否已经可以替代初级软件工程师？

---

## 已提供论文

[A] Gao, Tian et al. (2025). "Trae Agent: An LLM-based Agent for Software Engineering with Test-time Scaling." arXiv:2507.23370.
Identifier: arXiv:2507.23370

[B] Deng et al. (2025). "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?" arXiv:2509.16941.
Identifier: arXiv:2509.16941

[C] Becker, Rush, Barnes & Rein (2025). "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity." arXiv:2507.09089.
Identifier: arXiv:2507.09089

---

## 输出要求

只输出 3 行 CSV，不要输出表头，不要添加解释。

每行对应一篇候选论文，分别为 [D]、[E]、[F]。

CSV 字段顺序必须严格如下：

case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note

字段填写规则：

- `case_id` 固定填写：C5
- `run_id` 固定填写：R2
- `condition` 固定填写：arxiv_off
- `selected_tag` 只能填写：D / E / F
- `full_text_available` 如果无法确认，填写 `unknown`
- `topic_relevance` 留空
- `is_duplicate` 留空
- `is_tangential` 留空
- `valid_paper` 留空
- `selection_note` 留空
