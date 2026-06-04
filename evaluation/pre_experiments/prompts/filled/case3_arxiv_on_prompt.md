你是一名科研助理。你的任务不是撰写完整研究报告，而是为后续报告任务补充三篇候选论文。

你需要基于给定课题和已提供的三篇论文 [A]、[B]、[C]，自主检索并选择三篇额外论文，分别标记为 [D]、[E]、[F]。

## 硬性规则

- 不要撰写研究报告。
- 自主检索并确认候选论文的元信息。
- 不要写入 memory。
- 不要调用 write、edit、exec、process 等文件或命令工具；只在最终回复中输出 3 行 CSV。
- 不要选择与 [A]、[B]、[C] 重复或高度重复的论文。
- 不要选择只和课题“擦边相关”的论文。
- 优先选择 arXiv、bioRxiv 或其他可开放获取全文的论文。
- 优先选择 2024-2025 年的论文；如果更早论文明显更相关，也可以选择，但需要在标识符和年份字段中如实填写。
- 优先选择与 protein-ligand docking、binding affinity prediction、AI drug discovery、molecular generation、hit generation、wet-lab validation 或 docking benchmark generalization 直接相关的论文。
- 如果检索结果无法确认题名、年份或标识符，不要捏造；对应字段填写 `unknown`。

---

## 课题

AI 能否可靠预测蛋白质-配体结合亲和力，从而替代昂贵的湿实验筛选？

---

## 已提供论文

[A] Graber et al. (2025). "GEMS — Enhancing Generalizable Binding Affinity Prediction by Removing Data Leakage." bioRxiv:2024.12.09.627482.
Identifier: bioRxiv:2024.12.09.627482

[B] Osman et al. (2025). "From In Silico to In Vitro: Evaluating Molecule Generative Models for Hit Generation." arXiv:2512.22031.
Identifier: arXiv:2512.22031

[C] Morehead et al. (2025). "Deep Learning for Protein-Ligand Docking: Are We There Yet?" arXiv:2405.14108.
Identifier: arXiv:2405.14108

---

## 输出要求

只输出 3 行 CSV，不要输出表头，不要添加解释。

每行对应一篇候选论文，分别为 [D]、[E]、[F]。

CSV 字段顺序必须严格如下：

case_id,run_id,condition,selected_tag,paper_title,paper_id_or_url,year,full_text_available,topic_relevance,is_duplicate,is_tangential,valid_paper,selection_note

字段填写规则：

- `case_id` 固定填写：C3
- `run_id` 固定填写：{run_id}
- `condition` 固定填写：arxiv_on
- `selected_tag` 只能填写：D / E / F
- `full_text_available` 根据检索结果填写 `yes` / `no` / `unknown`
- `topic_relevance` 留空
- `is_duplicate` 留空
- `is_tangential` 留空
- `valid_paper` 留空
- `selection_note` 留空
