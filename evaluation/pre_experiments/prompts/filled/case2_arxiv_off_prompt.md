你是一名科研助理。你的任务不是撰写完整研究报告，而是为后续报告任务补充三篇候选论文。

你需要基于给定课题和已提供的三篇论文 [A]、[B]、[C]，选择三篇额外论文，分别标记为 [D]、[E]、[F]。

## 硬性规则

- 不要撰写研究报告。
- 只基于下面给定的课题和三篇已提供论文信息选择候选论文。
- 不要写入 memory。
- 不要调用 write、edit、exec、process 等文件或命令工具；只在最终回复中输出 3 行 CSV。
- 不要选择与 [A]、[B]、[C] 重复或高度重复的论文。
- 不要选择只和课题“擦边相关”的论文。
- 优先选择与 synthetic data training、model collapse、recursive training、LLM factual degradation、weak data 或 multimodal synthetic data 直接相关的论文。
- 如果你无法确认某篇论文的题名、年份或标识符，不要捏造；对应字段填写 `unknown`。

---

## 课题

用合成数据训练 LLM 是否会导致模型性能退化（model collapse）？

---

## 已提供论文

[A] Huang et al. (2025). "Knowledge Collapse in LLMs: When Fluency Survives but Facts Fail under Recursive Synthetic Training." arXiv:2509.04796.
Identifier: arXiv:2509.04796

[B] Amin, Babakniya, Bie, Kong, Syed & Vassilvitskii (2025). "Escaping Collapse: The Strength of Weak Data for Large Language Model Training." arXiv:2502.08924.
Identifier: arXiv:2502.08924

[C] Hu, Rostami & Thomason (2025). "Multi-modal Synthetic Data Training and Model Collapse: Insights from VLMs and Diffusion Models." arXiv:2505.08803.
Identifier: arXiv:2505.08803

---

## 输出要求

只输出 3 行 CSV，不要输出表头，不要添加解释。

每行对应一篇候选论文，分别为 [D]、[E]、[F]。

CSV 字段顺序必须严格如下：

case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note

字段填写规则：

- `case_id` 固定填写：C2
- `run_id` 固定填写：{run_id}
- `condition` 固定填写：arxiv_off
- `selected_tag` 只能填写：D / E / F
- `full_text_available` 如果无法确认，填写 `unknown`
- `topic_relevance` 留空
- `is_duplicate` 留空
- `is_tangential` 留空
- `valid_paper` 留空
- `selection_note` 留空
