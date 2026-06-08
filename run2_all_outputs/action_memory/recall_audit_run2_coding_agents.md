# Recall Audit — Run 2: AI Coding Agents vs Junior Software Engineers

## Audit 摘要
- case_id: exp_coding_agents_run2
- 总 claim 数: 5 (H1, H2, I1, I2, J1)
- 论文: [H] 2512.10218, [I] 2511.00197, [J] 2512.22087

## Audit 结果

### Claim H1: SWE-Bench-Verified 分数反映训练记忆
- **数据来源**: [H, Abstract]
- **原文检查**: "models performed 3 times better on SWE-Bench-Verified... 6 times better at finding edited files... task should be logically impossible to solve"
- **结论**: ✅ 正确。直接从 Abstract 提取，无 overclaim。

### Claim H2: 基准污染质疑泛化能力
- **数据来源**: [H, Abstract]
- **原文检查**: "benchmark scores may reflect training recall, not issue-solving skill... continues to be used in ways that can misrepresent progress"
- **结论**: ✅ 正确。扩展性解释合理（"calls for shift toward contamination-aware datasets" 在 Abstract 中明确）。

### Claim I1: Agent 成功取决于策略和近似修改
- **数据来源**: [I, Abstract]
- **原文检查**: "successful attempts employ distinct strategies... failed trajectories are consistently longer... 72-81% correct file identification... success depends more on achieving approximate rather than exact code modifications"
- **结论**: ✅ 正确。Abstract 中全部明确表述。无过解释。

### Claim I2: Agent 失败模式架构特异性
- **数据来源**: [I, Abstract]
- **原文检查**: "failure patterns differ significantly between agents" 在 Abstract 中明确。
- **结论**: ✅ 正确。扩展性解释（"scaffold determines failure mode"）是合理推论。

### Claim J1: 上下文管理作为可调用工具
- **数据来源**: [J, Abstract]
- **原文检查**: "elevates context maintenance to a callable tool... SWE-Compressor reaches a 57.6% solved rate... significantly outperforms ReAct-based agents"
- **结论**: ✅ 正确。57.6% 数据来自 Abstract。

## 总体统计
- ✅ 正确: 5/5 (100%)
- ❌ Overclaim: 0/5 (0%)
- ❌ Mis-citation: 0/5 (0%)
- ❌ Misattribution (1.96%/12.5% 混淆): 0/5 (0%)
