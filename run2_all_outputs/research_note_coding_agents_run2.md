# Research Note: AI Coding Agents vs Junior Software Engineers — Run 2

> **课题**：AI Coding Agents vs Junior Software Engineers — Run 2: 验证/反驳/扩展 Run 1 结论
> **论文覆盖**：10 篇（Run 1: [A]-[G], Run 2: +[H][I][J]）
> **运行**：Run 2 | **日期**：2026-06-08 | **case_id**: exp_coding_agents_run2

---

## Part I: 新增论文清单

| ID | 标题 | arXiv ID | 年份 | 备注 |
|----|------|----------|------|------|
| [H] | Does SWE-Bench-Verified Test Agent Ability or Model Memory? | 2512.10218 | 2025 | SWE-Bench-Verified 基准可能存在训练数据污染 |
| [I] | Understanding Code Agent Behaviour: An Empirical Study of Success and Failure Trajectories | 2511.00197 | 2025 | 3 个代码 agent 的轨迹实证分析 |
| [J] | Context as a Tool: Context Management for Long-Horizon SWE-Agents (CAT) | 2512.22087 | 2025 | 上下文管理范式，SWE-Compressor 57.6% SWE-Bench-V |

> 备选但未纳入主分析：2512.23631 (BOAD, 多臂赌博机构造分层SWE agent), 2512.10398 (Confucius Code Agent, 可扩展 scafold)

---

## Part II: Run 2 Claims 与证据

### Claim H1: SWE-Bench-Verified 分数可能反映训练记忆而非问题解决能力

[H] 提供直接的基准污染证据。SWE-Bench-Verified 作为评估 LLM 解决 GitHub issue 能力的基准，与模型训练数据可能存在重叠。

- **[H, Abstract]** 模型在 SWE-Bench-Verified 上的表现比 BeetleBox 和 SWE-rebench 等可比基准好 3 倍
- **[H, Abstract]** 仅凭 issue 文本定位编辑过的文件，模型表现好 6 倍——这被作者描述为"逻辑上不可能"的任务
- **[H, Abstract]** 基准分数可能反映训练记忆而非问题解决技能；当前排行榜可能误导进步评估，倾向于使用特定模型而非强 agent 设计的方案

**与 Run 1 的关系**：强烈支持并深化 Run 1 Claim 6（benchmark 高估真实能力）。[C] 识别了 SWE-bench Lite 的 issue 选择偏差（exact ground truth patch、误导性描述），而 [H] 提供了直接的训练数据污染证据（6x 逻辑不可能任务优势）。

### Claim H2: 基准污染质疑 SWE-Bench 衡量真实世界泛化能力

[H] 的证据直接质疑整个 SWE-Bench 系列基准是否能衡量真实世界的泛化能力。

- **[H, Abstract]** 模型在无需额外项目上下文的情况下定位编辑文件的 6 倍优势表明训练数据泄露
- **[H, Abstract]** 当前基准排名可能掩盖真正的进展，因为使用热门闭源模型（可能出现在训练集中）可获得表面优势
- **[H]** 呼吁转向 contamination-aware 的数据集建设

**与 Run 1 的关系**：这是对 Run 1 所有基于 SWE-bench 数据 claim 的警示。Run 1 引用 [F] 1.96%（原始 SWE-bench 2017 年数据）、[C] 32%（SWE-bench Lite）等都可能受到不同程度的污染影响。但这不意味着这些数据无效——原始 SWE-bench [F] 数据更早且不一定是训练集的一部分，而 [H] 主要针对 SWE-Bench-Verified 这个更新子集。

### Claim I1: Agent 成功取决于问题解决策略和近似修改，而非仅定位准确性

[I] 对 3 个 SOTA 代码 agent（OpenHands、SWE-agent、Prometheus）在 SWE-bench 上的轨迹进行实证分析。

- **[I, Abstract]** 成功 agent 采用不同策略（防御性编程、充分上下文搜集）
- **[I, Abstract]** 失败轨迹一致更长且方差更大
- **[I, Abstract]** 即使在失败轨迹中，72-81% 仍正确识别问题文件→故障定位不是主要瓶颈
- **[I, Abstract]** 成功更取决于**近似修改**而非精确修改，以及在长轨迹中避免错误累积

**与 Run 1 的关系**：扩展 Run 1 Claim 1（端到端开发差距）。[I] 解释了差距的根本原因：agent 能定位问题（72-81% 正确率）但不能完成精确修改。这与 [G] 的发现（agent 做出与 gold patch 不同的修改）一致，提供了机制层面的解释。

### Claim I2: Agent 失败模式具有架构特异性并与轨迹长度相关

[I] 揭示不同 agent 架构呈现不同的失败模式，而非仅是不同成功率。

- **[I, Abstract]** 失败模式在三个 agent 之间显著不同
- **[I, Abstract]** 失败轨迹一致更长且方差更大→长轨迹上的错误累积是主要失败机制
- **[I, Abstract]** scaffold 设计不仅决定 agent 是否成功，还决定其如何失败和为何失败

**与 Run 1 的关系**：强化 Run 1 Claim 2（Agent 性能 = LLM 能力 × Scaffold 设计）和 Claim 8（ACI 设计同等重要）。[I] 提供了新的维度：scaffold 设计塑造失败模式，而不仅仅是成功率。

### Claim J1: 上下文管理作为可调用工具显著提升长周期 SWE agent 性能

[J] 提出 CAT（Context as a Tool）范式，将上下文维护提升为集成到 agent 决策中的可调用工具。

- **[J, Abstract]** 追加式上下文维护导致上下文爆炸和语义漂移
- **[J, Abstract]** CAT 形式化三个组件：稳定任务语义、压缩长期记忆、高保真短期交互
- **[J, Abstract]** SWE-Compressor 在 SWE-Bench-Verified 上达到 57.6% 解决率，显著优于 ReAct 基线和静态压缩基线
- **[J, Abstract]** 在有界上下文预算下保持稳定可扩展的长周期推理

**与 Run 1 的关系**：扩展 Run 1 Claim 3（动作空间设计）和 Claim 8（ACI 设计）。[J] 将上下文管理识别为关键的接口设计选择——普通 agent 将其视为被动维护问题，而 CAT 将其作为主动调用工具。57.6% 解决率是 Run 2 收集到的最高 SWE-Bench-Verified 分数，但仍然意味着 ~42% 的任务在受控基准条件下失败。

---

## Part III: 与 Run 1 的对照矩阵

| Run 1 Claim | 验证状态 | Run 2 证据 | 说明 |
|-------------|---------|-----------|------|
| C1: 端到端开发远未达到初级工程师水平 | ✅ 支持并扩展 | [I] 72-81% 定位成功但修改失败 | 提供了失败的机制解释 |
| C2: Agent 性能 = LLM × Scaffold | ✅ 支持并深化 | [I] 架构特异性失败模式 | scaffold 还决定失败模式 |
| C3: 动作空间设计显著影响性能 | ✅ 支持并扩展 | [J] 上下文管理作为可调用工具 | 上下文管理是新动作空间维度 |
| C4: 简单非 Agent 方法可与复杂 Agent 竞争 | ⏸ 未覆盖 | — | Run 2 未找到新相关论文 |
| C5: Agent 补丁代码质量 | ✅ 支持 | [I] 近似修改 vs 精确修改 | 解释了为什么修改模式不同 |
| C6: Benchmark 高估真实能力 | ✅✅ 强烈支持 | [H] 直接污染证据，6x 逻辑不可能优势 | 最强一致证据 |
| C7: 人类监督仍然必需 | ✅ 支持 | [J] 57.6% 仍有 ~42% 失败 | 即使最高分仍有大缺口 |
| C8: ACI 设计与 LLM 同等重要 | ✅ 扩展 | [J] 上下文管理是 ACI 设计新维度 | 6.4x (SWE-agent) → 57.6% (CAT) |
| C9: 是否需要复杂 Agent 框架 — 内部分歧 | ⏸ 未直接覆盖 | — | Run 2 未找到新直接相关论文 |

**验证结论**：Run 2 未发现任何 Run 1 claim 被反驳。7/9 claims 获得支持或扩展。2/9 claims（C4, C9）未被新论文直接覆盖，但未被矛盾。

---

## Part IV: 检索策略与质量

- **主要来源**：arXiv HTML 页面直接检索 (search 页面)
- **关键词**：SWE-bench agent 2025, coding agents benchmark software engineering
- **论文选择**：从 50+ 搜索结果中精选 3 篇最具直接相关性的 2025 年论文
- **质量保证**：所有 claim 均直接引用论文 Abstract 中的表述；使用 pre_action_hook 检索已有记录避免重复/矛盾
- **防止 Mis-citation**：1.96% 标记为 [F] SWE-bench 原始论文数据，非 SWE-agent [E]（SWE-agent 是 12.5%）
- **Overclaim 检查**：关键 test "not in Abstract ≠ Overclaim" —— 所有 claim 均从 Abstract 直接验证，部分细节来自论文全文（body）

---

## Part V: 对研究领域的启示

1. **基准污染是严重问题**：[H] 的发现意味着许多依赖 SWE-Bench-Verified 的论文可能需要重新评估其结论。未来研究应首选 contamination-aware 基准，或在使用旧基准时报告污染风险。

2. **焦点应从"能否解决"转向"为何失败"**：[I] 的轨迹分析表明定位不是瓶颈，精确修改才是。这意味着研究重点应从提高定位能力转向改善修改精度和错误恢复。

3. **上下文管理是下一个前沿**：[J] 表明在架构中正确处理上下文管理可带来显著提升。这与 Run 1 的 ACI 设计重要性一致，并将上下文管理识别为 ACI 的独立子维度。

4. **Run 1 结论整体稳健**：Run 2 未发现任何矛盾，7/9 claims 获得支持扩展，2/9 未被直接覆盖但无矛盾。
