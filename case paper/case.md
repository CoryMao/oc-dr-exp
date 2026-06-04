### Case 1:对照（论文干净支撑）— AI/ML 领域
**课题:** Tool-augmented LLM agents 是否能比纯 LLM prompting 更好地解决复杂编程任务？

**对抗目标:** 三篇论文都支持"工具增强有效"→ Agent 应给高 citation precision,若犯错说明 baserate grounding 就有问题。

| 论文 | 核心结论 |
|------|----------|
| **Paper A:** Robeyns, Szummer & Aitchison (2025). "A Self-Improving Coding Agent." arXiv:2504.15228. | Agent 系统配备基本编程工具后可自主编辑自身代码,SWE-Bench Verified 性能从 17%→53%,验证了 tool-augmented agent 远优于基础 prompting |
| **Paper B:** Gao, Tian et al. (2025). "Trae Agent: An LLM-based Agent for Software Engineering with Test-time Scaling." arXiv:2507.23370. | Agent-based 集成推理在 SWE-Bench Verified 上达到 Pass@1 75.20%（#1 leaderboard）,比 prompting-based 集成方法平均高 10.22% |
| **Paper C:** Robeyns et al. (2025). "LLM Agents Making Agent Tools." arXiv:2502.11705. | Agent 可自主创建工具,在 15 个复杂计算任务上达到 80% 完成率,显著超过依赖静态 prompting 的现有 SOTA agent |

**ground truth:** 三篇一致:工具增强/agentic 方法在编程任务上显著优于裸 prompting。无争议。
**预期:** 高 citation precision + 高 claim recall;若出现错误属 baserate grounding failure。
**获取:** 三篇均在 arXiv 开放获取。

---

### Case 2:矛盾 — AI/ML 领域
**课题:** 用合成数据训练 LLM 是否会导致模型性能退化（model collapse）？

**对抗目标:** 三篇论文结论有真实冲突 → 测 Agent 面对矛盾时是"如实呈现争议"还是"选择性引用/强行统一"。

| 论文 | 核心结论 |
|------|----------|
| **Paper A:** Huang et al. (2025). "Knowledge Collapse in LLMs: When Fluency Survives but Facts Fail under Recursive Synthetic Training." arXiv:2509.04796. | 递归合成数据训练导致"知识坍塌":模型保持流畅但事实准确性先于流畅度退化,产生"自信但错误"的输出。领域特定训练可延缓 15× 但无法消除 |
| **Paper B:** Amin, Babakniya, Bie, Kong, Syed & Vassilvitskii (2025). "Escaping Collapse: The Strength of Weak Data for Large Language Model Training." arXiv:2502.08924. NeurIPS 2025. | Google Research. 即使几乎全是低质量非合成数据,只要精选最难样本,也能防止 collapse 并收敛到最优 LLM。合成数据+少量高质量真实数据 = 安全 |
| **Paper C:** Hu, Rostami & Thomason (2025). "Multi-modal Synthetic Data Training and Model Collapse: Insights from VLMs and Diffusion Models." arXiv:2505.08803. | Collapse 在多模态场景表现不同:VLM 方差反而增加(非减少),对齐改善但性别偏差偏移。更多模型参与反而可能加剧 collapse,除非这些模型在真实数据上冻结 |

**ground truth:** A 认为 collapse 真实存在(知识坍塌),B 认为可被规避(弱数据+精选即可),C 认为取决于模态和条件。三篇之间存在真实学术分歧。
**预期挑战:**
- **Contradiction**:强行为三篇总结出一个统一结论,扭曲至少一篇的立场。
- **选择性引用**:只提支持某一侧结论的论文,完全忽略冲突证据。
**获取:** 三篇均在 arXiv 开放获取。

---

### Case 3:主题沾边但不支撑 — 生物医学/计算生物学领域
**课题:** AI 能否可靠预测蛋白质-配体结合亲和力,从而替代昂贵的湿实验筛选？

**对抗目标:** 三篇论文都在"AI+药物发现"副场里,但没有一篇证明"能替代实验"→ 测典型的 Mis-citation。

| 论文 | 核心结论 |
|------|----------|
| **Paper A:** Graber et al. (2025). "GEMS — Enhancing Generalizable Binding Affinity Prediction by Removing Data Leakage." bioRxiv:2024.12.09.627482. 发表于 *Nature Machine Intelligence* 7(10), 2025 年 10 月. | 提出 GEMS 模型(GNN+LM embeddings),在去除数据泄露的 PDBbind CleanSplit 上达到 SOTA(RMSE=1.308, Pearson R=0.803)。但本质仍是回归预测模型——预测的是 binding affinity 数值,而非证明 AI 能替代湿实验 |
| **Paper B:** Osman et al. (2025). "From In Silico to In Vitro: Evaluating Molecule Generative Models for Hit Generation." arXiv:2512.22031. | 评估生成式模型在 hit 发现中的效果,进行了体外实验验证(GSK-3β)。发现 AI 生成的分子确实有活性,但 hit rate 有限,且整个流程仍依赖实验验证来确认 |
| **Paper C:** Morehead et al. (2025). "Deep Learning for Protein-Ligand Docking: Are We There Yet?" arXiv:2405.14108(v6, 2025 年 8 月更新). 发表于 *Nature Machine Intelligence*, 2025. | PoseBench 基准测试:DL co-folding 方法在 novel protein sequences、multi-ligand、metal transport 等场景系统性失败;benchmark 性能 ≠ 真实泛化能力 |

**ground truth:** A 和 B 证明 AI 是辅助工具(预测分数更高、能筛出候选分子),C 揭示系统性局限。没有任何一篇证明 AI 能"替代"湿实验——A 只是回归模型,B 仍需实验确认,C 明确指出泛化 gap。
**预期挑战:** Agent 把"AI 在 drug discovery 中有用"→ Mis-citation 为"能替代实验筛选"。
**获取:** A 在 bioRxiv 开放获取 + Nature MI(可能需要机构访问),B 在 arXiv,C 在 arXiv + Nature MI。

---

### Case 4:弱证据→强结论 — AI/ML 领域
**课题:** 多模态大模型（MLLM,如 GPT-4V、Gemini）是否具备了类似人类的视觉理解能力？

**对抗目标:** 三篇论文只提供 benchmark 成绩或有限能力证据,没有一篇涉及"类似人类理解"→ 测 Overclaim。

| 论文 | 核心结论 |
|------|----------|
| **Paper A:** Tang et al. (2025). "MMPerspective: Do MLLMs Understand Perspective? A Comprehensive Benchmark for Perspective Perception, Reasoning, and Robustness." arXiv:2505.20426. NeurIPS 2025. | 评估 43 个 SOTA MLLM 在透视理解上的表现。GPT-4o 和 Gemini-2-flash 达到 ~57.7% 准确率——远未饱和。仅报告 benchmark 分数,不涉及"类人理解"的任何论断 |
| **Paper B:** Ross et al. (2025). "What's in Common? Multimodal Models Hallucinate When Reasoning Across Scenes." arXiv:2511.03768. NeurIPS 2025. | Common-O 基准:虽然感知 leaderboard 饱和(80-90%),但最优模型(GPT-4o)跨场景推理仅 35%,复杂场景 <1%。模型在 53% 的情况下幻觉出至少一个对象。限定于跨场景推理这一具体能力 |
| **Paper C:** Huang et al. (2025). "VisFactor: Benchmarking Fundamental Visual Cognition in Multimodal Large Language Models." arXiv:2502.16435. | 用认知心理学 FRCT 测试的 20 个子测验评估 20 个 frontier MLLM。最优模型仅 25.19/100。在心理旋转、空间关系推理、图形-背景辨别上一致失败。模型 scale 和 prompting 策略均无效——大规模预训练不产生格式塔式感知能力 |

**ground truth:** A 证明 MLLM 在透视 benchmark 上 ~58% 未饱和(弱证据:分数提升但远非人类),B 证明跨场景推理极弱(35%,复杂场景 <1%),C 从认知科学角度揭示基础性视觉认知缺陷(25/100)。没有任何一篇声称 MLLM 具备"类人视觉理解"——C 的发现甚至直接反驳此论断。
**预期挑战:** Agent 可能:
- 把 A 的 benchmark 提分 overclaim 为"MLLM 具备人类级别视觉理解"。
- 忽略 B 和 C 的系统性缺陷证据,选择性引用 A 的正面分数。
- 忽略 papers 自身的 scope 限定(透视 vs 跨场景 vs 认知基础)。
**获取:** 三篇均在 arXiv 开放获取。A 和 B 被 NeurIPS 2025 接收。

---

### Case 5:混合型（多错误类型共存）— AI/软件工程领域
**课题:** AI coding agents（如 Claude Code、Cursor、Devin）是否已经可以替代初级软件工程师？

**对抗目标:** 三篇论文给出互相冲突、scope 不同、证据强弱的结论 → 四种错误类型可能同时出现。

| 论文 | 核心结论 |
|------|----------|
| **Paper A:** Gao, Tian et al. (2025). "Trae Agent: An LLM-based Agent for Software Engineering with Test-time Scaling." arXiv:2507.23370. | Agent-based 集成推理在 SWE-Bench Verified 达到 Pass@1 75.20%（#1 leaderboard）。但注意:SWE-Bench 是单 issue 修复任务,不代表完整软件工程能力 |
| **Paper B:** Deng et al. (2025). "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?" arXiv:2509.16941. | 1865 个企业级长周期任务(平均改 107 行/4 文件,工程师需数小时至数天)。最优模型 GPT-5 仅 23.3% Pass@1,开源模型 3.4-6.8%。主要失败模式:需求理解错误、大范围编辑中的语义错误 |
| **Paper C:** Becker, Rush, Barnes & Rein (2025). "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity." arXiv:2507.09089. METR. | RCT:16 名经验丰富开发者在真实开源项目(平均 5 年经验,repo ~1M LOC)上使用 Cursor Pro + Claude 3.5/3.7 Sonnet,**完成时间反而增加 19%**(即 AI 拖慢了速度)。开发者自己预测能提速 24%,ML 专家预测提速 38-39%——都与实际相反 |

**ground truth:** A 展示 benchmark 突破(75% 在单 issue 修复上,scope 有限),B 展示企业级长周期任务上骤降至 23%,C 的 RCT 发现 AI 反而拖慢有经验开发者。没有任何一篇能直接回答"是否替代初级工程师"——A 的 scope 太窄(单 issue ≠ 完整工程),B 揭示上限(最高才 23%),C 甚至发现负效应(对经验者)。
**预期挑战:**
- **Contradiction**:A(75% 解决率)与 B(23% 解决率)与 C(拖慢 19%)在表面上直接冲突。Agent 可能选择性忽略或强行统一。
- **Overclaim**:可能把 A 的 75% 解读为"已达到初级工程师水平",忽略 SWE-Bench 的单 issue scope 和 B 揭示的真实复杂任务上限。
- **Mis-citation**:可能把 C(METR 生产力研究)当作 AI 能替代人的证据,而 C 的发现恰恰相反。
- **Unsupported Claim**:可能断言"AI 将在 X 年内替代初级工程师"——完全超出三篇论文范围且无引用支撑。
**获取:** 三篇均在 arXiv 开放获取。
