# Research Note: AI Coding Agents vs Junior Software Engineers — Run 1

> **课题**：系统性文献综述 — AI coding agents（Claude Code, Copilot, Devin, Cursor, SWE-agent 等）能否替代初级软件工程师？
> **多维度分析**：task 覆盖度（bug fix、feature implementation、code review、test generation）、代码质量（correctness, security, maintainability）、human oversight 需求
> **运行**：Run 1 | **日期**：2026-06-08 | **论文覆盖**：7 篇（2023-2026）

---

## Part I: 论文清单

| ID | 标题 | arXiv ID | 年份 | 备注 |
|----|------|----------|------|------|
| [A] | Agent Psychometrics: Task-level Performance Prediction in Agentic Coding Benchmarks | 2604.00594 | 2026 | IRT 分解 LLM 与 scaffold 能力 |
| [B] | ProjDevBench: Benchmarking AI Coding Agents on End-to-End Project Development | 2602.01655 | 2026 | 端到端项目开发，27.38% 通过率 |
| [C] | Agentless: Demystifying LLM-based Software Engineering Agents | 2407.01489 | 2024 | 简单非 Agent 管线 32% SWE-bench Lite |
| [D] | CodeAct: Executable Code Actions Elicit Better LLM Agents | 2402.01030 | 2024 (ICML) | Python code action 空间高 20% |
| [E] | SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | 2405.15793 | 2024 | ACI 设计显著提升 6.4x |
| [F] | SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | 2310.06770 | 2024 (ICLR) | 原始基准，最佳模型仅 1.96% |
| [G] | Evaluating Software Development Agents: Patch Patterns, Code Quality, and Issue Complexity in Real-World GitHub Scenarios | 2410.12468 | 2024 (SANER 2025) | 4892 patches，代码质量分析 |

---

## Part II: Claims 与证据

### Claim 1: 端到端开发远未达到初级工程师水平

AI coding agents 在端到端项目开发中以初级软件工程师水平仍存在巨大差距。

- **[B, Abstract]** ProjDevBench 报告 27.38% 整体接受率。agent 能处理基本功能和数据结构，但在复杂系统设计、时间复杂度优化和资源管理方面失败。
- **[F, Abstract]** SWE-bench 上最佳模型（Claude 2）仅解决 1.96% 的真实 GitHub issue，这些 issue 通常需要跨多个函数、类乃至文件的协调修改。
- **[C, Abstract]** 即使在简化的 SWE-bench Lite 上，最佳方法（Agentless）也仅达到 32%。

**一致性评估**：三个基准证据高度一致（27.38%、1.96%、32%），量化了端到端能力缺口。注意 SWE-bench Lite 是简化子集（去除有 exact ground truth patch 或误导性描述的issues），因此 32% 可能高估真实能力。

### Claim 2: Agent 性能 = LLM 能力 × Scaffold 设计

Agent Psychometrics **[A]** 引入 IRT（Item Response Theory）分解 agent 能力为 LLM 能力分量和 scaffold 能力分量。此参数化允许跨异构排行榜聚合评估数据，并预测未见过的 LLM-scaffold 组合的任务级性能 **[A, Abstract]**。

- **[A]** 证明当前排名主要反映 scaffold/benchmark 选择，而非内在 agent 能力。
- **[E]** SWE-agent 证实：定制 ACI 设计将 SWE-bench 性能从 1.96%（非交互式）提升至 12.5%（6.4x 提升），展示 scaffold 设计的选择与 LLM 同等重要。

### Claim 3: Action space 设计显著影响性能

CodeAct **[D]** 显示可执行 Python 代码作为统一动作空间在 17 个 LLM 上比 JSON/文本替代方案高最多 20% 的成功率 **[D, Abstract]**。

- Python 解释器支持动态代码执行、自我修正和工具组合。
- 动作空间表示形式的工程选择对 agent 有效性有显著影响，独立于底层 LLM。

### Claim 4: 简单的非 Agent 方法可与复杂 Agent 竞争

Agentless **[C]** — 一个简单的三阶段管线（定位、修复、补丁验证），无需 LLM 驱动的工具使用或自主规划 — 在 SWE-bench Lite 上达到 32.00%（96 个经正确修复），成本低至 $0.70，超越所有开源软件 agent **[C, Abstract]**。

- 这与需要复杂 agent 框架的假设直接矛盾。
- 但该简单方法仅解决了 ~1/3 的简化 benchmark issue，真实性能可能更低（因 Lite-S 子集排除问题后[由该文自行构造]）。

### Claim 5: Agent 生成补丁的代码质量 — 安全性维持但复杂性增加

**[G]** 分析了来自 10 个顶级 agent 在 500 个真实 GitHub issue 上的 4,892 个补丁：

- 多数 agent 维持了代码可靠性和安全性，避免了新 bug 或漏洞
- 一些 agent 增加了代码复杂度，但许多减少了代码重复和代码异味
- 170/500 个 issue 未被任何 agent 解决
- Agent 比 gold patch 做出不同文件和函数修改，暴露出 benchmark 测试覆盖率不足
- Agent 在更简单的代码库上表现更好，提示将复杂任务拆分为子任务可提升效果

### Claim 6: Benchmark 可能高估真实世界能力

多项证据表明 benchmark 通过率高估真实能力：

- **[C]** 识别 SWE-bench Lite 中存在 exact ground truth patch 或误导性描述的 issue，构造 SWE-bench Lite-S 进行更严格评估
- **[G]** agent 做出与 gold patch 不同的修改，显示 benchmark 测试覆盖率不完整
- **[B]** 端到端项目 27.38% 与 SWE-bench Lite 32% 形成对比，确认 bug-fix benchmark 与完整项目开发间的差距

### Claim 7: 人类监督仍为必要 — Human-in-the-Loop

所有论文汇聚于同一结论：人类监督仍然必需。

- **[B]** ~73% 端到端任务仍失败
- **[G]** 170/500 个 issue 未被任何 agent 解决
- **[F]** Claude 2 仅 1.96% SWE-bench 通过率
- **[A]** LLM+scaffold 双因子模型显示两者均未达到复杂任务的人类级非确定性推理水平

**结论**：当前 coding agents 作为人类辅助工具而非替代品。

### Claim 8: ACI 设计与 LLM 模型选择同等重要

SWE-agent **[E]** 的定制 ACI 设计带来 6.4x 提升（从 1.96% 到 12.5%），证明 agent-环境交互的工程设计与底层 LLM 选择同等重要。**[A]** 以 IRT 将其形式化为分离的 LLM 能力和 scaffold 能力参数。

### Claim 9: 是否需要复杂 Agent 框架 — 文献内部分歧

- **[C]** 主张不需要：简单非 agent 管线（处理->定位->修复->验证）即可达到最高性能
- **[D]** 主张丰富动作空间提升 20%
- **[E]** 主张定制 ACI 带来 6.4x 提升

**解析**：这并非矛盾 — 分歧在于"agent 自主性的最优级别是 task-dependent"。**[C]** 的非 agent 方法在结构化 bug-fix 上有效但无法泛化到端到端开发 **[B]**。

---

## Part III: 关键分歧

| 分歧点 | 观点 A | 观点 B | 解析 |
|--------|--------|--------|------|
| 是否需要 agent 框架 | [C] 简单非 agent 管线 32%，不需要 | [D][E] 丰富动作空间/Custom ACI 显著提升 | 任务依赖：bug-fix 可非 agent，端到端需 agentic |
| Benchmark 是否可靠 | [C] SWE-bench Lite 需要清理 | [F] 原始 benchmark 已是 gold standard | [C] 自行构造 Lite-S 验证了偏差存在 |
| 代码质量是否可接受 | [G] 多数 agent 维持安全性和可靠性 | [G] 170/500 未解决 + 修改模式不同于 gold patch | 结果混合：pass-rate 层面可接受但模式层面有问题 |

---

## Part IV: 检索策略

- **主要来源**：arXiv 直接搜索已知 ID（HTML abstract），Web search (timed out, 改用 arXiv search API)
- **关键词**：coding agents, SWE-bench, LLM software engineering, code quality, agent psychometrics, ProjDevBench, CodeAct
- **论文选择标准**：聚焦 peer-reviewed 或 high-profile arXiv 论文（ICML, ICLR, SANER）
- **补充**：从之前的 Research Note（Case 5）继承了 4 篇论文 [A-D] 的核心结论，新增 3 篇 [E-G] 覆盖更全面维度
