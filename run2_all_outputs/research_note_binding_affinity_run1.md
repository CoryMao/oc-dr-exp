# 研究笔记：蛋白质-配体结合亲和力预测计算方法比较（Run 1）

## 论文清单

| 标签 | 论文 | arXiv | 方法类型 |
|------|------|-------|----------|
| [A] | Morehead & Cheng, "Assessing the potential of deep learning for protein-ligand docking" (PoseBench) | 2405.14108 | DL 基准（DL co-folding vs 传统对接） |
| [B] | Rossi et al., "Fast and Accurate Binding Affinity Prediction through Coarse Structural Representations" (TerraBind) | 2602.07735 | DL 粗粒表征结合亲和力预测 |
| [C] | Kopko et al., "Evaluating Learnable Protein-Ligand Scoring Functions on Unseen Targets" | 2512.05386 | ML 评分函数泛化能力 |
| [D] | Osman et al., "From In Silico to In Vitro: Evaluating Molecule Generative Models for Hit Generation" | 2512.22031 | DL 生成模型 + 对接打分 |
| [E] | Wan & Coveney, "On the Reliability of AI Methods in Drug Discovery: Evaluation of Boltz-2 for Structure and Binding Affinity Prediction" | 2603.05532 | AI vs 物理方法（Boltz-2 vs ESMACS） |
| [F] | Gao et al., "Are 2D fingerprints still valuable for drug discovery?" | 1911.00930 | 传统 ML（RF/GBDT/DNN）vs 3D DL |

## 关键发现

### 一、基于物理的方法
- 分子对接（AutoDock Vina）在 PoseBench 中被 DL co-folding 方法全面超越 [A §3.1]
- ESMACS（增强采样 MM/GBSA）提供可重复的结合自由能估计，含统计不确定性量化和 UQ，这是 AI 方法普遍缺乏的 [E §1]
- FEP 可提供严格结合自由能估计，但计算代价极高，不适用于大规模虚拟筛选 [C §2]
- AI 方法（Boltz-2）与 ESMACS 仅弱到中度相关，top-100化合物无显著相关性 [E §2.2]

### 二、基于传统 ML 的方法
- 2D fingerprint + RF/GBDT/DNN 在毒性、溶解度、分配系数和 ligand-only 亲和力预测上表现与 3D 方法相当 [F Abstract]
- 但在 complex-based（结构感知）亲和力预测中被 3D 方法超越 [F Abstract]
- 标准基准（CASF-2016, DUD-E）存在数据泄漏，ML 评分函数在新靶点上性能急剧下降 [C §1]

### 三、基于深度学习的方法
- DL co-folding 方法（Chai-1, Boltz-1, AF3）在结构预测上全面超越传统对接 [A §3.1]
- 但在新型/OOD 靶点上表现显著下降（AF3 在 DockGen-E 上 >50% 失败）[A §3.2]
- AF3 高度依赖 MSA，Boltz-1/Chai-1 则不敏感 [A §3.1-3.3]
- TerraBind 证明粗粒表征足以进行亲和力预测，26×加速且提高 20% Pearson r [B Abstract]
- TerraBind 提供校准的不确定性估计（epinet）[B §2.3]

### 四、关键矛盾
- TerraBind 认为全原子扩散对结合亲和力预测不必要（粗粒就够）[B §1]，而 PoseBench 发现 DL co-folding（全原子）在结构预测上最优 [A §3.1]
- Wan et al. 认为 AI（Boltz-2）缺乏先导识别的能量分辨率，必须依赖物理方法进行精炼 [E Abstract]，而 TerraBind 声称在亲和力预测上超越 Boltz-2 20% [B Abstract]
- Kopko et al. 指出标准基准存在泄漏导致性能高估 [C §1]，而 PoseBench 使用的 DockGen-E 和 CASP15 在一定程度上缓解了该问题 [A §3.4-3.5]

### 五、计算成本对比
| 方法 | 推理时间 | 参数量 | 适用场景 |
|------|---------|--------|---------|
| 传统对接 (AutoDock Vina) | 分钟级 | N/A | 快速初筛 |
| ESMACS (MM/GBSA) | 小时级（多副本） | N/A | 先导识别/优化 |
| FEP | 天级 | N/A | 先导优化（小规模） |
| DL co-folding (Boltz-2, AF3) | ~20s/复合物 | ~509M | 中等规模筛选 |
| TerraBind | ~0.76s/复合物 | ~30M | 超大规模筛选 |
| 2D fingerprint + ML | 秒级 | 小 | 无结构筛选 |
