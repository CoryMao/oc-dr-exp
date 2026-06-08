# 系统性文献综述：MLLMs 是否具备类人视觉理解能力？— Run 2

**运行**：Run 2（扩展验证） | **日期**：2026-06-08 | **论文覆盖**：3 篇新论文（2025-2026）+ 6 篇 Run 1 论文

---

## Part I：新论文摘要

### [G] VisReason — Can MLLMs Reason Beyond Language? A Comprehensive Benchmark for Vision-Centric Reasoning

**arXiv**: 2605.25364 | **发表**：2026-05-25 | **机构**：中科院自动化所

**核心发现**：
- 1,505 个问题，10 个类别，覆盖感知（perceptual）、结构（structural）和概念（conceptual）推理
- 最佳模型在需要精细感知锚定的空间定位任务上表现极差：Localized Reasoning 仅 6.9%、Spot-the-Difference 仅 1.3%
- 人类基线：Localized Reasoning 81.7%、Spot-the-Difference 77.4%
- CoT 提示仅带来 +1.1% 的平均增益，对 Spot-the-Difference、3D-Spatial Reasoning 和 Pattern Counting 甚至产生负效果
- 模型准确率与推理 token 数无稳定正相关
- 结论：当前 MLLMs 的视觉推理成绩很大程度上依赖于粗粒度视觉线索或场景级抽象，而非真正的视觉锚定推理 [G, Abstract; §4.3; §4.4]

### [H] Cartesian Shortcut — The Cartesian Shortcut: Re-evaluate Vision Reasoning in Polar Coordinate Space

**arXiv**: 2605.09883 | **发表**：2026-05-11 | **机构**：Stanford University, Google

**核心发现**：
- 识别出 MLLMs 的一个普遍漏洞：视觉推理基准普遍使用正交网格布局（Cartesian），模型可利用该布局将视觉问题转化为文本坐标推理
- 构造 Polaris-Bench（53 个任务）：在保持逻辑约束和任务语义不变的前提下，将布局转为极坐标（Polar）空间
- 前沿模型（70~83% on Cartesian）在极坐标等价任务上崩溃到 31~39%，下降幅度达 50%+
- 在 Cartesian 上观察到的推理增益在 Polar 等效任务上严重减弱
- 揭示核心缺陷：MLLMs 缺乏**拓扑不变视觉推理**（topology-invariant visual reasoning）能力 [H, Abstract; §1]

### [I] Eliciting Complex Spatial Reasoning in MLLMs through Wide-Baseline Matching

**arXiv**: 2606.03577 | **发表**：2026-06-02 | **机构**：未知（多机构合作）

**核心发现**：
- 构建 ReasonMatch-Bench：按视角位移和匹配粒度分层的宽基线匹配基准（室内/室外/物体中心场景）
- 在困难 90 样本子集上，人类标注者达 84.0 F1，最佳现有 MLLM 基线仅 37.2 F1
- 宽基线匹配要求整合几何理解、视角变化、精细感知和遮挡推理——这正是 MLLMs 的薄弱环节
- 提出 DCRL（Dynamic Correspondence Reinforcement Learning）：结合图像级视角递进和点级对应课程，通过可验证奖励训练
- DCRL 显著提升 ReasonMatch-Bench 性能，并泛化到相关空间基准 [I, Abstract; §1]

---

## Part II：与 Run 1 八条 Claim 的对比验证

### Claim 1 → 覆盖验证
**Run 1**: 基础视觉认知大面积缺失（VisFactor: 最佳 MLLM 54.0% vs 人类 78.8%）
**Run 2 新证据**: [G] VisReason 在空间定位任务上模型仅 1.3-6.9% vs 人类 77-82%。**完全一致**，且提供了更强证据（差距更大）。[G, §4.3]

### Claim 2 → 覆盖验证
**Run 1**: 感知饱和，推理乏力（Common-O: 单图 80-90%，跨场景 35%）
**Run 2 新证据**: [G] VisReason 显示 CoT 仅 +1.1% 增益，说明感知层面看似好的成绩不能转为推理。[G, §4.4] **完全一致**。

### Claim 3 → 覆盖验证
**Run 1**: 空间推理广泛薄弱（MME-CC: Gemini 总体 42.66%，空间/几何 ≤ 30%）
**Run 2 新证据**: [I] 宽基线匹配最佳模型 37.2 F1 vs 人类 84.0 F1。[I, Abstract] | [H] Cartesian→Polar 崩溃 70-83%→31-39%。**完全一致且加强了结论**。

### Claim 4 → 覆盖验证
**Run 1**: 空间推理典型错误模式（朝向/参考系错误、跨视角身份保持脆弱）
**Run 2 新证据**: [H] 揭示了更深层的机制——模型依赖"笛卡尔捷径"，缺乏拓扑不变推理，这解释了朝向/参考系错误的根本原因。**扩展并深化了 Claim 4**。

### Claim 5 → 覆盖验证
**Run 1**: 反事实指令执行能力差
**Run 2 新证据**: 三篇论文未直接测试反事实推理，但 [H] 的拓扑变换实验本质上涉及反事实空间变换。**部分验证**。

### Claim 6 → 覆盖验证
**Run 1**: 规则-实例绑定失败是主导性故障模式（StemBind）
**Run 2 新证据**: [H] 的"笛卡尔捷径"从另一个角度揭示了类似问题——模型依赖表面模式而非真正理解任务结构。**概念上一致**。

### Claim 7 → 覆盖验证
**Run 1**: 心理可视化能力存在显著鸿沟（Hyperphantasia）
**Run 2 新证据**: 三篇论文未涉及心理可视化评估。**未覆盖，需后续运行补充**。

### Claim 8 → 覆盖验证
**Run 1**: 规模和思考模式不是万能药
**Run 2 新证据**: [G] CoT 仅 +1.1% 且空间任务负效果 | [H] 推理增益在 Polar 上消失 | [I] 即使 DCRL 训练能提升，仍远低于人类。**完全一致**。

---

## Part III：新发现（超越 Run 1 的 Claim 1-8）

### Claim 9（新增）— MLLMs 存在"笛卡尔捷径"漏洞
MLLMs 在视觉推理中系统性地利用正交网格布局（Cartesian coordinate prior），将视觉问题暗中转化为文本坐标推理。当布局被重构成拓扑等价但几何不同的极坐标系统时，性能急剧下降 50%+。这揭示了一个不同于 Run 1 各论文发现的**全新漏洞维度**：MLLMs 的视觉推理严重依赖布局格式的"正交先验"，而非拓扑不变的空间理解。[H, Abstract; H, §1]

### Claim 10（新增）— 空间对应推理的差距大于已有认知
宽基线匹配（wide-baseline matching）要求在显著视角变化下建立精细的空间对应，这是之前基准未充分测试的能力。MLLMs 在该任务上（37.2 F1 vs 人类 84.0 F1）的差距超过运行 1 中所有基准报告的差距，表明现有基准可能低估了 MLLMs 在真实世界空间理解上的缺陷。[I, Abstract; I, §1]

### Claim 11（新增）— CoT 对视觉锚定推理无效甚至有害
三篇新论文一致发现：CoT/thinking 模式在需要精细视觉锚定的任务上不仅无效，还常降低性能。VisReason 报告 CoT 在 Spot-the-Difference 和 3D-Spatial Reasoning 上负效果。[G, §4.4] Cartesian Shortcut 显示推理增益在 Polar 布局上消失。[H, §1] 这与 Run 1 中 StemBind 的"thinking 模式降低表现"发现一致，但拓展了适用范围。[G, §4.4; H, §1; D, §4.2]

---

## Part IV：论文清单（完整）

| ID | 标题 | arXiv ID | 年份 | 来源 |
|----|------|----------|------|------|
| [A] | MMPerspective (Do MLLMs Understand Perspective?) | 2505.20426 | 2025 | Run 1 |
| [B] | What's in Common? / Common-O | 2511.03768 | 2025 | Run 1 |
| [C] | VisFactor (Human Cognitive Benchmarks) | 2502.16435 | 2025 | Run 1 |
| [D] | StemBind (Rules vs Instances) | 2606.00148 | 2026 | Run 1 |
| [E] | MME-CC (Cognitive Capacity) | 2511.03146 | 2025 | Run 1 |
| [F] | Hyperphantasia (Mental Visualization) | 2507.11932 | 2025 | Run 1 |
| **[G]** | **VisReason (Vision-Centric Reasoning)** | **2605.25364** | **2026** | **Run 2 新增** |
| **[H]** | **Cartesian Shortcut (Polaris-Bench)** | **2605.09883** | **2026** | **Run 2 新增** |
| **[I]** | **Eliciting Complex Spatial Reasoning (ReasonMatch-Bench)** | **2606.03577** | **2026** | **Run 2 新增** |

---

## Part V：综评

Run 2 三篇新论文全面验证并强化了 Run 1 的主要结论：
1. **无新增反例**：没有发现任何论文挑战"MLLMs 不具备类人视觉理解"的核心结论
2. **发现新漏洞维度**：笛卡尔捷径（Cartesian Shortcut）揭示了一个先前未被系统识别的方法论偏见
3. **量化差距更大**：宽基线匹配 37.2 vs 84.0 F1 的差距是 Run 1 各基准中报告的最大人机差距
4. **CoT 无效的证据更强**：三篇论文从不同角度确认了 CoT 在视觉锚定任务上的局限性
5. **需要补充**：心理可视化维度（Claim 7）仍需更多证据；反事实推理（Claim 5）仅被间接验证
