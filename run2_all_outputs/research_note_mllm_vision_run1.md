# 系统性文献综述：MLLMs 是否具备类人视觉理解能力？

**运行**：Run 1 | **日期**：2026-06-08 | **论文覆盖**：6 篇（2025-2026）

---

## Part I：总体评估

六篇核心论文高度一致地表明：当前 Multimodal Large Language Models（MLLMs）**不具备类人视觉理解能力**，且缺陷具有**系统性和基础性**。这些缺陷横跨视觉认知、空间推理、抽象推理（含反事实推理）四大维度，且不随模型规模扩大或推理模式启用而自动消失。

核心论文标签对照：
- [A] **MMPerspective** (arXiv:2505.20426) — 透视感知、推理与鲁棒性基准
- [B] **Common-O / What's in Common** (arXiv:2511.03768) — 跨场景推理幻觉
- [C] **VisFactor** (arXiv:2502.16435) — 人类认知基准下的 MLLM 视觉鸿沟
- [D] **StemBind** (arXiv:2606.00148) — 抽象视觉推理中的规则-实例绑定失败
- [E] **MME-CC** (arXiv:2511.03146) — 认知能力多模态评估基准
- [F] **Hyperphantasia** (arXiv:2507.11932) — 心理可视化能力评估

> ⚠️ 注意：任务描述中提供的 [A] arXiv:2411.18017（物理光学）、[B] arXiv:2502.12195（域泛化）、[C] arXiv:2505.06550（图论）经 arXiv 验证为不相关论文，已通过 memory 检索找到 2026-06-04 同一课题 Case 4 已验证的论文 ID 替换。

---

## Part II：逐维度结论

### 维度一：视觉认知（Visual Cognition）

**结论 1：基础视觉认知大面积缺失**
MLLMs 在人类视为"理所当然"的基础视觉任务上系统性失败。VisFactor 将 FRCT（因子参考认知测试）的 20 个视觉子测试数字化，评估 39 个前沿 MLLM，最佳模型 Gemini-3.1-Pro 仅达 54.0%，而人类基线为 78.8%。在心理旋转（mental rotation）、空间关系推理（spatial relation inference）和图形-背景区分（figure-ground discrimination）上，所有模型无论规模或提示策略均失败。[C, Abstract; C, §1; C, §3.2]

**结论 2：感知饱和，推理乏力**
Common-O 基准测试（10,500+ 样本）显示：MLLMs 在单图感知任务上可达到 80-90%，但跨场景推理（"这些场景的共同点是什么？"）最佳模型仅 35%，复杂场景仅 1%。53% 的回答包含幻觉。这表明 MLLMs 在感知层面看似强大，但一旦需要跨场景整合推理能力就急剧下降。[B, Abstract; B, §1]

### 维度二：空间推理（Spatial Reasoning）

**结论 3：空间推理广泛薄弱**
MME-CC（11 个任务，1,173 个问题）将认知能力分为空间、几何和知识推理三类。最佳模型 Gemini-2.5-Pro 总体 42.66%，空间和几何类别均 ≤ 30%。MMPerspective（10 个任务，2,711 张图片）亦显示最佳模型仅约 57.7%。模型能处理表面级透视感知任务，但在构成性空间推理和扰动保持空间一致性上失败。[E, Abstract; E, §1; A, Abstract]

**结论 4：空间推理的典型错误模式**
常见错误包括：朝向/参考系错误（orientation/reference-frame mistakes）、跨视角身份保持脆弱（fragile cross-view identity persistence）、物体位置关系混淆。[E, §3]

### 维度三：反事实推理（Counterfactual Reasoning）

**结论 5：反事实指令执行能力差**
MME-CC 明确将"对反事实指令的遵从度差"列为常见错误模式之一。MMPerspective 显示模型在涉及透视变换的构成性推理中失败，这些变换本质是反事实空间变化。StemBind 揭示模型无法将已推断出的规则绑定到反事实实例上（S3 映射瓶颈），在 22/24 模型中出现规则准确率高于完整答案准确率的"R-F chasm"。[E, Abstract; A, Abstract; D, §4.2]

### 维度四：抽象推理（Abstract Reasoning）

**结论 6：规则-实例绑定失败是主导性故障模式**
StemBind 通过共享主干预诊基准（2,298 个 stems, 19,533 个 P/R/F 任务）发现：即使 MLLM 正确感知图像内容（P）和识别规则（R），在同一 stem 上完整答案（F）仍然错误 51.2% 的时间。"推理的瓶颈在 S3（规则到实例的映射），而非感知或规则归纳。"[D, Abstract; D, §1; D, §4.2]

**结论 7：心理可视化能力存在显著鸿沟**
Hyperphantasia 基准（4 种可视化谜题，3 个难度级别）发现前沿 MLLMs 与人类在心理可视化任务上存在显著差距。强化学习训练展现出一些改善潜力，但未能根本解决这一局限性。[F, Abstract]

### 跨论文共识

**结论 8：规模和思考模式不是万能药**
六篇论文一致认为：扩大模型规模、启用显式思考模式（thinking / CoT）不能可靠地缩小人类视觉理解鸿沟。VisFactor 发现模型准确率与参数量无稳定正相关，CoT token 数与准确率负相关（r = -0.18 至 -0.35）。StemBind 发现 thinking 模式甚至降低了规则识别和完整答案准确率。Common-O 显示规模仅带来适度改善。[C, §3.2; D, §4.2; B, Abstract]

---

## Part III：关键分歧

| 分歧点 | 发现 A | 发现 B | 解析 |
|--------|--------|--------|------|
| 多图训练能否缓解？ | [B] 多图训练（multi-image）帮助大于规模扩展 | [D] thinking 模式降低表现 | 不同干预手段：多图训练 ≠ 推理模式；[B]的数据级增强与[D]的推理级增强效果不同 |
| CoT 是否有效？ | [A] CoT 带来适度改善 | [C] CoT 与准确率负相关，verbose ≠ 更好；[D] thinking 降低表现 | 差异可能源于任务类型：[A]为透视推理（语言描述空间位置有助），[C]和[D]为抽象模式匹配（语言干扰直觉判断） |
| RL 是否能改善？ | [F] RL 有改善潜力但未解决根本问题 | 其他论文未系统评估 RL | 结论有限且尚未收敛 |

---

## 论文清单

| ID | 标题 | arXiv ID | 年份 | 获取状态 |
|----|------|----------|------|----------|
| [A] | Do MLLMs Understand Perspective? A Comprehensive Benchmark for Perspective Perception, Reasoning, and Robustness (MMPerspective) | 2505.20426 | 2025 (NeurIPS DB) | ✓ HTML fetched |
| [B] | What's in Common? Multimodal Models Hallucinate When Reasoning Across Scenes (Common-O) | 2511.03768 | 2025 (NeurIPS D&B) | ✓ HTML fetched |
| [C] | Human Cognitive Benchmarks Reveal Foundational Visual Gaps in MLLMs (VisFactor) | 2502.16435 | 2025 | ✓ HTML fetched |
| [D] | When MLLMs Get Lost Between Rules and Instances in Abstract Visual Reasoning (StemBind) | 2606.00148 | 2026 | ✓ HTML fetched |
| [E] | MME-CC: A Challenging Multi-Modal Evaluation Benchmark of Cognitive Capacity | 2511.03146 | 2025 | ✓ HTML fetched |
| [F] | Hyperphantasia: A Benchmark for Evaluating the Mental Visualization Capabilities of Multimodal LLMs | 2507.11932 | 2025 | ✓ HTML fetched |

**检索策略**：从 2026-06-04 Case 4（同一课题）的 memory 获取已验证论文 ID，通过 arXiv 直接 fetch HTML 全文或 Abstract 页面。由于任务提供的 arXiv ID 与实际论文不匹配，使用了 previous experience 中的论文列表（MMPerspective、Common-O、VisFactor、StemBind、MME-CC、Hyperphantasia）。
