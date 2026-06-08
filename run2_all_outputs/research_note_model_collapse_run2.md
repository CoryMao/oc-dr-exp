# Research Note: Model Collapse in LLMs — 新进展与补充证据（Run 2）

> **课题**：Model Collapse in LLMs: Empirical Evidence and Mitigation Strategies
> **运行**：Run 2
> **生成时间**：2026-06-08 23:05 CST
> **case_id**: exp_model_collapse_run2

---

## Part I: Run 1 论文回顾（6 篇核心论文 [A]-[F]）

| ID | 标题 | arXiv ID | 作者 | 发表 |
|----|------|----------|------|------|
| [A] | The Curse of Recursion: Training on Generated Data Makes Models Forget | 2305.17493 | Shumailov et al. | 2023 |
| [B] | Model Collapse Demystified: The Case of Regression | 2402.07712 | Dohmatob et al. | 2024, ICML |
| [C] | A Tale of Tails: Model Collapse as a Change of Scaling Laws | 2402.07043 | Dohmatob et al. | 2024, ICML |
| [D] | Is Model Collapse Inevitable? | 2404.01413 | Gerstgrasser et al. | 2024 |
| [E] | Strong Model Collapse | 2410.04840 | Dohmatob et al. | 2024 |
| [F] | Beyond Model Collapse: Scaling Up with Synthesized Data Requires Verification | 2406.07515 | Feng, Dohmatob et al. | 2024 |

Run 1 完成 6 条 claim 提取、3 个关键分歧分析、4 个开放问题识别。详见 `research_note_model_collapse_run1.md`。

---

## Part II: Run 2 新增论文（3 篇，2025-2026）

| ID | 标题 | arXiv ID | 作者 | 发表 |
|----|------|----------|------|------|
| [G] | Demystifying Synthetic Data in LLM Pre-training: A Systematic Study of Scaling Laws, Benefits, and Pitfalls | 2510.01631 | Kang et al. | EMNLP 2025 |
| [H] | Recursive Training Loops in LLMs: How training data properties modulate distribution shift in generated data? | 2504.03814 | Kovač et al. | EMNLP 2025 (Oral) |
| [I] | A Probabilistic Perspective on Model Collapse | 2505.13947 | Xu et al. | 2025 |

---

## Part III: 各论文核心主张与 Claim 映射

### [G] Kang et al. 2025 (EMNLP) — Demystifying Synthetic Data in LLM Pre-training

**Claim G1 — Mixed evidence on model collapse in single-round pre-training** [G, Abstract]

The large-scale empirical study (>1000 LLMs, >100k GPU hours) found mixed evidence on model collapse during single-round (n=1) pre-training:
- Rephrased synthetic data alone → no degradation in performance at foreseeable scales
- Textbook-style pure-generated synthetic data → shows patterns predicted by model collapse (higher downstream loss)
- This contextualizes model collapse as dependent on synthetic data *type* and *generation method*, not merely presence of synthetic data

**Claim G2 — Optimal synthetic ratio ~30% for rephrased data** [G, Abstract]

- 1/3 rephrased synthetic data + 2/3 natural web text → 5-10x pre-training speedup at larger data budgets
- Optimal ratio converges to ~30% for rephrased synthetic data, depending on model size and data budget
- Larger generator models (>8B parameters) do not necessarily yield better pre-training data

### [H] Kovač et al. 2025 (EMNLP Oral) — Recursive Training Loops in LLMs

**Claim H1 — Lexical diversity amplifies distribution shift; semantic diversity and data quality mitigate** [H, Abstract]

First empirical examination of how human training data properties modulate distribution shift magnitude in recursive LLM training:
- Lexical diversity → amplifies distribution shifts (worsens model collapse)
- Semantic diversity and data quality → mitigate shifts
- Highly modular: data from one internet domain has little influence on content from another domain
- Different parts of the internet may undergo different types of distribution shift

**Claim H2 — Political bias amplification or reduction depends on data properties** [H, Abstract]

- Human data properties determine whether initial political bias is amplified or reduced through recursive training
- Demonstrates distribution shift is not a uniform degradation phenomenon
- Provides a more nuanced view than simple "model collapse leads to degradation"

### [I] Xu et al. 2025 — A Probabilistic Perspective on Model Collapse

**Claim I1 — Superlinear sample size growth necessary to prevent collapse** [I, Abstract]

Conceptualizes recursive parametric model training as a *random walk of the model estimate*:
- Progressively increasing sample size at each training step is necessary to prevent model collapse
- Under unbiased estimation: required growth rate is superlinear (faster than linear)
- Under estimation bias: required growth rate must be accelerated even further
- Provides precise mathematical condition for collapse avoidance

**Claim I2 — Conditions under which synthetic training outperforms real-only** [I, Abstract]

- Investigates the probability that recursive synthetic training outperforms real-data-only training
- With appropriate sample size growth and limited estimation bias, synthetic training can match/exceed real-only baselines
- Extends results to general parametric model families in an asymptotic regime

---

## Part IV: Run 1 vs Run 2 交叉验证

### 对比 1: Kang [G] vs Dohmatob [E] — 合成数据比例与崩溃关系

| | [E] Dohmatob 2024c (Strong Model Collapse) | [G] Kang 2025 (Demystifying Synthetic Data) |
|---|---|---|
| **核心主张** | 即使 1% 合成数据也能引发强模型崩溃 | Rephrased synthetic data 单独使用无 degradation |
| **看似矛盾** | 是，[E] 称 1% 即可崩溃，[G] 称 100% rephrased 也无问题 |
| **解析** | **训练范式不同**。[E] 分析多轮递归训练（固定合成比例），[G] 分析单轮混合预训练（n=1）。[G] 的 "textbook-style" 合成数据确实表现出 collapse 模式，与 [E] 一致。[G] 的 "rephrased" 数据因保留原始分布结构，不触发 collapse 机制。两者结论在各自框架下成立，不矛盾。 |

### 对比 2: Kovač [H] vs Shumailov [A] — 模型崩溃的影响因素

| | [A] Shumailov 2023 (Curse of Recursion) | [H] Kovač 2025 (Recursive Training Loops) |
|---|---|---|
| **扩展方向** | 定义 model collapse，在 VAE/GMM/LLM 中验证 | 深入分析 **什么因素** 调节分布偏移的严重程度 |
| **一致性** | 完全一致。[H] 不挑战 [A] 的结论，而是提供细粒度的调节因子分析 |
| **新贡献** | — | 首次实证揭示词汇多样性→放大偏移；语义多样性和数据质量→缓解偏移；领域间模块化效应 |

### 对比 3: Xu [I] vs Gerstgrasser [D] — 避免崩溃的数学条件

| | [D] Gerstgrasser 2024 (Is Model Collapse Inevitable?) | [I] Xu 2025 (Probabilistic Perspective) |
|---|---|---|
| **方法** | 实证 + 扩展线性模型框架 | 概率随机游走视角，严格数学证明 |
| **结论关系** | 积累策略→测试误差有限上界 | 样本量必须超线性增长→避免崩溃 |
| **数学深化** | [I] 为 [D] 的实证发现提供了严格的概率论基础，证明样本量增长率是避免崩溃的关键充分必要条件 |

### 新发现的分歧

**分歧 4: 模型崩溃的条件性**

- [E] (Dohmatob 2024c): 固定合成比例下，即使极小比例也必然崩溃
- [G] (Kang 2025): 某些合成数据类型（rephrased）在单轮预训练中不触发崩溃

**解析**: 模型崩溃不仅是"有/无合成数据"的问题，还取决于:
1. 合成数据类型（rephrased vs textbook-generated）
2. 训练范式（单轮混合 vs 多轮递归）
3. 样本量增长率（Xu [I] 的理论条件）
4. 人类数据属性（Kovač [H] 的调节因子）

---

## Part V: 开放问题更新

1. **[新] 合成数据类型分类学**：rephrased vs generated-textbook vs other types 在递归训练中的行为差异，需要系统分类。
2. **[新] 样本量增长策略在实际训练中的应用**：Xu [I] 的理论条件如何与 Gerstgrasser [D] 的积累策略结合？
3. **[新] 数据属性调节的因果机制**：Kovač [H] 发现的相关性需要因果验证——是因还是果？
4. **验证器可靠性界限**（Run 1 遗留）: 未在 Run 2 论文中直接解决。
5. **混合策略（验证器+积累）的最优设计**（Run 1 遗留）：Run 2 论文提供补充证据但未直接解决。

---

## Part VI: Methodological Notes

- **检索方法**：arXiv API（export.arxiv.org），避免 web scraping 超时
- **论文选择标准**：2025-2026 年发表，不在 [A]-[F] 范围内，直接涉及 model collapse in LLMs
- **Overclaim 防护**：每条 claim 对应具体论文字段 [G/H/I, Abstract] 定位，避免超出 abstract 的泛化
- **交叉验证**：逐条对比 Run 1 与 Run 2 claim，识别 4 组关系（一致、扩展、形式化、条件性差异）

---

*Generated by subagent for exp_model_collapse_run2*
