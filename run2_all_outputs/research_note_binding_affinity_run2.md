# 研究笔记：蛋白质-配体结合亲和力预测计算方法比较（Run 2）

## 论文清单（新增）

| 标签 | 论文 | arXiv | 方法类型 |
|------|------|-------|----------|
| [G] | Reddy & Liu, "ShallowBench: Benchmarking Generative Drug Design Models on Shallow-Pocket Targets" | 2606.06717 | 生成模型基准（浅口袋） |
| [H] | Wei et al., "HonestAffinity: Leak-Aware Evaluation of Protein and Pocket Priors for Binding Affinity Prediction" | 2606.03422 | 结合亲和力预测泄漏评估 |
| [I] | Meng et al., "A Large-Scale Dataset and Benchmark: Do Protein-Ligand Models Learn Binding Sites or Just Binding Likelihood?" | 2605.24045 | 结合位点定位 vs 结合概率基准 |

## Run 1 延续论文清单 [A]-[F]

| 标签 | 论文 | arXiv | 方法类型 |
|------|------|-------|----------|
| [A] | Morehead & Cheng, "Assessing DL for protein-ligand docking" (PoseBench) | 2405.14108 | DL 基准 |
| [B] | Rossi et al., "Fast and Accurate Binding Affinity Prediction" (TerraBind) | 2602.07735 | DL 粗粒表征 |
| [C] | Kopko et al., "Evaluating Learnable Scoring Functions on Unseen Targets" | 2512.05386 | ML 评分函数泛化 |
| [D] | Osman et al., "From In Silico to In Vitro: Evaluating Molecule Generative Models" | 2512.22031 | DL 生成模型 |
| [E] | Wan & Coveney, "Reliability of AI Methods: Boltz-2 for Structure and Binding Affinity" | 2603.05532 | AI vs 物理方法 |
| [F] | Gao et al., "Are 2D fingerprints still valuable for drug discovery?" | 1911.00930 | 传统 ML vs 3D DL |

## 新增关键发现

### [G] ShallowBench — 浅口袋靶点的生成模型困境
- 生成式 AI 药物设计模型在深口袋上表现良好，但低凹度（浅口袋）靶点上预测结合亲和力显著下降 [G Abstract]
- ShallowBench 从 CrossDocked2020 中筛选出 5,780 个浅口袋靶点，通过 Alpha Shape "盖" 体积与蛋白原子体素体积的差异量化凹度 [G Abstract]
- 历史性 "不可成药" 靶点如 KRAS 和 MYC 属于典型的低凹度目标，现有 SOTA 在此类靶点上性能不足 [G Abstract]
- 需要新的架构创新或损失函数设计以处理这些挑战性靶点 [G Abstract]
- **与 Run 1 的关联**：确认了 [A] PoseBench 的 OOD 泛化失败结论，但从生成药物设计角度提供了新的靶点类型视角

### [H] HonestAffinity — 泄漏感知评估与分裂条件反转
- 标准 PDBbind 风格拆分存在跨折叠的相似性泄漏，导致对先验（pocket marker、ESM-2 嵌入）效果的误判 [H Abstract]
- 核心发现是 **split-conditioned reversal**：pocket marker 和 ESM-2 嵌入在常规验证集和 CASF-2016 拆分上改善 Pearson R，但在严格无泄漏分层测试集（test_cl1-cl3）上反而降低 Pearson R [H Abstract]
- HonestAffinity-Pocket-NoESM（不含 ESM-2 嵌入、含 pocket marker）在每层严格无泄漏测试集上取得最佳平均 Pearson R [H Abstract]
- 提出模型应同时报告常规和无泄漏消融结果，部署场景匹配的变体优于单一默认模型 [H Abstract]
- **与 Run 1 的关联**：直接支持 [C] Kopko 关于基准泄漏的批评，并提供了具体的新证据——泄漏不仅高估性能，还会翻转先验效果排名

### [I] InteractBind — 结合位点定位 vs 结合概率的定性分离
- 包含约 100k 蛋白质-配体对的大规模数据集，支持细粒度评估 [I Abstract]
- 核心细粒度任务：结合位点定位，使用蛋白残基-配体原子相互作用图谱覆盖 6 种非共价相互作用类型 [I Abstract]
- 评估 8 个现有序列感知和相互作用感知模型：**二元结合预测能力强，但结合位点定位能力有限** [I Abstract]
- 非共价相互作用类型之间表现出显著差异 [I Abstract]
- 结论：当前模型学习的是**结合概率**而非实际的结合位点位置 [I Abstract]
- **与 Run 1 的关联**：引入了一个 Run 1 完全未覆盖的新评估维度——解释性/物理合理性，对将 DL 方法用于先导识别提出了更深层次的质疑

## 跨 Run 对比分析

### 一、结论一致性
- **OOD 泛化困难**（[A], [C], [G] 一致支持）：三个独立工作从不同角度确认了 DL/ML 方法在新靶点上的性能下降
- **基准泄漏问题**（[C], [H] 一致支持）：标准基准存在系统性问题，HonestAffinity 进一步揭示了泄漏对先验评估方向性的影响
- **物理方法价值**（[E] Boltz-2 vs ESMACS 相关弱，[I] 结合位点定位不足）：均指向纯数据驱动方法的根本性局限

### 二、新矛盾与发现
- **HonestAffinity 的反直觉结果**：传统的 "更多先验=更好" 假设在无泄漏评估下不成立 —— pocket marker 和 ESM-2 在严格条件下反而是有害的
- **生成模型不仅仅是精度问题**：ShallowBench 指出即使在亲和力预测层面，特定靶点类型（浅口袋）存在系统性的结构瓶颈
- **可解释性成为新维度**：InteractBind 将评估从相关性指标扩展到物理合理性，揭示即使是高性能模型也无法正确定位结合位点

### 三、局限性
- [G] ShallowBench 仅评估 CrossDocked2020 的一个子集，未涉及泛化到其他数据源
- [H] HonestAffinity 基于 LP-PDBBind（~11.5k 复合物），规模有限，结论是否推广到更大规模数据有待验证
- [I] InteractBind 的 8 个模型主要来自 2024 年前的方法，未包含最新的 DL co-folding 方法

## 新增 Claims

### Claim 10 — ShallowBench: 浅口袋靶点困境 [G]
生成式 AI 药物设计模型在浅口袋（低凹度）靶点上预测结合亲和力显著弱于深口袋靶点。ShallowBench 从 CrossDocked2020 中提供 5,780 个浅口袋靶点，SOTA 模型在 KRAS、MYC 等历史不可成药靶点上性能不足。（来源：[G, Abstract]）

### Claim 11 — HonestAffinity: 分裂条件反转 [H]
结合亲和力评估中存在分裂条件反转：pocket marker 和 ESM-2 嵌入在常规 PDBbind 拆分上改善 Pearson R，但在严格无泄漏分层测试集上反而降低。HonestAffinity-Pocket-NoESM 在每层严格无泄漏测试集上取得最佳平均 Pearson R。（来源：[H, Abstract; H, §Results]）

### Claim 12 — InteractBind: 结合位点定位不足 [I]
蛋白质-配体相互作用模型表现出二元结合预测能力强但结合位点定位能力有限的定性分离。在 InteractBind 基准（约 100k 对）上，8 个评估模型在六种非共价相互作用类型间表现出显著差异——当前模型学习结合概率而非实际结合位点位置。（来源：[I, Abstract; I, §Results]）

## 方法论反思
- Run 2 搜索到 3 篇非常新的论文（均为 2026 年 5-6 月），说明该领域发展迅速
- HonestAffinity 的可复现性检查（split-conditioned reversal）是值得注意的发现
- 与 Run 1 的 claims 无冲突，且新 claims 从三个新增维度（靶点几何、评估泄漏、可解释性）补充了结论
