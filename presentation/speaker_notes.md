# OpenClaw 引用一致性评测 Presentation 讲稿

这份讲稿对应 `openclaw_deepresearch_overview.pdf` 的 33 页版本。默认口径是 12-18 分钟汇报；如果时间更短，可以优先讲第 1-6、14-16、20-22、27-31、33 页。

## 1. 标题页

大家好，我们这次项目关注的是 OpenClaw 科研 Agent 在生成科研报告时的引用一致性问题。更具体地说，我们不是只看它有没有给引用，而是看这些引用是否真的能够支撑报告中的结论。
我们最后搭建了一套可复现的评测流程，包括 prompt、skills、MCP 工具、memory 机制、运行日志、输出格式和后续错误统计。

## 2. 项目目标

这页定义整个项目的核心问题：OpenClaw 搭建的科研 Agent 会不会出现“引用与结论不一致”。
这里的关键点是，报告里的结论看起来有引用支持，但实际检查引用材料后，可能发现引用只能支持一个更弱的说法，或者支持的是另一个任务、另一个数据集，甚至和结论方向相反。
所以我们的目标不是改 Agent 内部代码，而是从外部设计一套实验，让这个问题可以被稳定复现、记录、标注和统计。

## 3. 被测系统

这页展示系统架构。输入是五个科研主题和部分固定 PDF 材料，OpenClaw Agent 使用 DeepSeek v4 Pro 作为基模，并接入 PDF skill、arxiv MCP、refchecker MCP、citation-standard skill 和 Brave web search。
Agent 输出带标准引用的科研报告。对于 memory 条件，我们只把 refchecker repair log 中的结构化记录写入 JSONL memory，再在后续 case 中检索注入。
这里要强调：memory 不是原文证据，也不是聊天历史延续，而是结构化的“以前犯过什么引用错误”的经验。

## 4. Agent 报告结构

为了让评测可自动化，我们强制报告输出四段 marker：`ORIGINAL_REPORT`、`REFCHECKER_REPAIR_LOG`、`REPAIRED_REPORT` 和 `RUN_SUMMARY`。
其中 original report 是初稿，repair log 是结构化 JSONL 核查记录，repaired report 是修复后的报告。
这个设计的好处是，后续可以用脚本稳定抽取 claim-citation pair，而不是从自由文本里猜哪里是结论、哪里是引用。

## 5. 五个 Case

我们选了五个主题，覆盖 coding agent、合成数据和 model collapse、蛋白-配体 docking、多模态认知 benchmark、AI coding tools。
这个设计的目的有两个：第一，避免只测一个熟悉的 CS topic；第二，不同 case 的证据形态不同，有些是 benchmark 数值，有些是实验结论，有些是用户研究或领域专业 claim。
这样更容易暴露“元数据正确但语义支撑不足”的问题。

## 6. citation-standard skill

这页是实验能不能复现的关键。我们使用 citation-standard skill 规定引用位置必须写成 CPS，也就是标签加定位，例如 `[A] §4.1::¶2` 或 `[C] p7§5.1::F4`。
这样可以避免“见 abstract”“第 5 页附近”“limitations 部分”这种不可解析的引用。
后续人工标注和脚本统计都依赖这个标准化格式，因为我们要比较的是 claim 和具体 citation scope 之间是否一致。

## 7. 整体实验流程

整体流程是：准备 case 和 prompt，Agent 先生成 original report，然后用 refchecker 和原文阅读做核查，生成 repair log 和 repaired report。
如果是 memory 条件，repair log 会被抽取成 active memory。下一次运行前，memory 会被检索出来拼到 prompt 前面，作为 procedural caution。
所以这个流程同时支持两件事：一是比较 repair 前后有没有改善；二是看之前的 repair 经验能否减少后续错误。

## 8. arxiv MCP 预实验

arxiv MCP 预实验的目的，是看 Agent 能否自主找到合适的 [D][E][F] 三篇论文。
我们做了 arxiv off 和 arxiv on 两个条件，每个 case 三次运行。记录的不是最后报告质量，而是 Agent 选出来的论文是否真实、是否相关、是否可获取全文、是否重复或偏题。
这一步主要是工具验证：如果文献获取工具本身不稳定，后面的主实验就会被基础设施噪声污染。

## 9. arxiv-MCP 贴合分数测试

这里的结果比较反直觉：arxiv MCP 开关与论文主题贴合度并没有明显正相关，有些 case 甚至 on 的分数更低。
但这不一定说明 arxiv MCP 没用。它更像是提高“能否找到真实论文和元数据”的工具，而不是一个 relevance optimizer。
尤其 Case 5 下降明显，说明 AI coding tools 这个主题本身检索空间很散，Agent 容易找到相关但不够核心的论文。

## 10. 为什么结果合理

这页解释 arxiv MCP 的真实作用边界。它能帮助找到论文、减少幻觉引用、提供元数据，但不能保证每次找到最贴题的文献。
换句话说，arxiv MCP 解决的是“paper existence and access”的问题，不解决“paper selection optimality”的问题。
所以在主实验里，我们把它作为固定工具，而不是把 relevance 结果直接解释成 Agent 推理能力。

## 11. Case 5 机制

Case 5 的困难来自主题分散。AI coding tools 可以指 developer productivity、SWE-Bench、Copilot adoption、workflow、代码质量等很多方向。
这些方向都相关，但不一定支撑同一个核心问题。因此 Agent 很容易选到“主题相关但证据不直接”的论文。
这也提醒我们：引用一致性问题不只来自模型胡编，也来自任务边界过宽时的证据选择偏移。

## 12. arxiv 可视化

这页主要看图。我们不需要过度解释每个柱子，重点说两点：第一，arxiv on 不是稳定提高贴合度；第二，case-level 差异很明显。
结论是后续主实验不能简单假设“开工具就一定提高质量”，必须把工具能力和 Agent 的证据选择能力分开看。

## 13. refchecker repair 预实验

refchecker 预实验的目标是看它作为生成期工具是否能帮助 repair。每次运行要求 Agent 输出 original report 和 refchecker repair 后的 repaired report。
refchecker 的强项是核查论文是否存在、标题作者年份是否匹配、DOI/arXiv ID 是否正确。
但它不能直接判断“这段引用是否支撑这个结论”，所以我们仍然要求 Agent 读原文做 claim support 检查。

## 14. Memory MVP 主实验

主实验的 memory 条件最终只跑 P1 和 P2 两轮，每轮按 C1 到 C5 的固定顺序运行。
memory 的来源非常克制：只写入 repair log，不写完整报告，不写人工标注，也不把 memory 当科学证据引用。
我们的研究问题是：如果 Agent 看到之前 case 中的引用错误和修复动作，它会不会在后续报告里更谨慎。

## 15. Memory 机制

这页是实际 memory 实现。每个 case 完成后，我们从 `REFCHECKER_REPAIR_LOG` 抽取 JSONL 行，规范化为 `active_memory.jsonl`。
下一个 case 开始前，脚本用当前 case 的 topic 和关键词做 TF-IDF-like 词匹配检索，默认取 top-6，然后把结果注入 prompt 的 `MEMORY_CONTEXT` 区块。这里要注意：正式主实验没有用 BM25；BM25 是早期 `scripts/retrieve.py` action-memory 草案支持的方法，但主实验走的是 `retrieve_memory_context.py`。
这个 context 明确说明只能作为 procedural caution，不能作为证据引用。

## 16. Memory 实现细节

这里可以更技术一点。run 前，`retrieve_memory_context.py` 读取共享 JSONL，用 query：case id、topic、citation、metadata、support、overclaim、scope_error、refchecker、repair、CPS 等词来检索。它的排序是 TF-IDF-like token scoring，再额外 boost 有错误类型、有修复动作、同 case 命中的记录。
每次最多取 6 条，context 最长 5000 字符。run 后，只有输出 marker 完整且没有 hard failure，才从 repair log 中抽 JSONL 写回。
最终 memory 有 97 条记录。注意 retrieve log 会保留 retry 和调试历史，所以正式分析时要按最终 P1/P2 的 run log 和 manifest 过滤。

## 17. 可复现材料

这页说明我们交付的不只是结果图，而是完整实验材料。
包括 prompt、profile setup、preflight audit、run manifest、stderr、raw output、citation validator、memory retrieval/writeback 脚本。
核心原则是：别人应该能知道每个 run 用了什么工具配置、什么 prompt、什么输入材料、最后输出在哪里。

## 18. 运行环境与工具链问题

实验过程中遇到很多非模型能力的问题。比如 arXiv DNS 和代理问题、Brave search 配置漂移、arxiv MCP 偶发 `-32000`、DeepSeek auth 在 profile 之间不一致等。
这些问题如果不控制，会被误判成 Agent 能力差。
所以我们固定代理环境、统一 Brave provider、使用 safe wrapper，并且每个 profile 做 audit。

## 19. 工具链如何约束实验设计

这页总结工程风险如何影响实验设计。比如并行运行会放大 timeout，所以主实验固定 `JOBS=1`。
workspace 和 memory 污染会破坏变量隔离，所以每个 run 要有明确 session key，memory 只在 M1 条件下按顺序共享。
输出格式漂移会导致统计不可复现，所以固定四段 marker 和 CPS 引用格式。

## 20. refchecker repair 效果

这里进入结果。我们用 `evaluation/judge` 流水线做 LLM-as-judge 评测：抽取 claim-citation pair，构造 batch，然后用 DeepSeek 批量判定。
结果是 refchecker repair 前后总错误数 40 到 40，没有减少。只有 C1 有改善，C2 和 C4 甚至增加，C3 和 C5 持平。
这说明 refchecker repair 不是自动提高报告可信度的充分条件。

## 21. 错误类型全景

这页看错误类型分布。我们主要关注 unsupported claim、overclaim、mis-citation 和 contradiction。
图里的重点不是某一个柱子，而是错误类型在不同 case 之间高度不均匀。
特别是 C3 这种专业领域，unsupported claim 明显更突出。

## 22. 错误类型关键发现

C3 的 unsupported claim 是主力，原因是这些 claim 的引用元数据往往是正确的，但语义支撑不成立。
这暴露了 refchecker 的能力边界：它能验证论文是否存在、作者标题年份是否正确，但不能判断一个蛋白-配体 docking 的定量结论是否被证据充分支撑。
所以我们的核心结论之一是：citation verification 不等于 claim verification。

## 23. Failure Case：Mis-citation

这页给出 mis-citation 的直观例子。它不是完全乱引，而是“沾边但接不上”。
比如引用论文主题相关，但讨论的是不同任务、不同设定或不同结论范围。
这种错误很隐蔽，因为读起来像是有学术来源，只有检查具体 citation scope 才能发现不支撑。

## 24. Failure Case：Overclaim 和 Contradiction

Overclaim 是结论强于原文证据，比如把单次实验结果推广成普遍规律，或者把用户反馈分析说成因果结论。
Contradiction 更严重，指引用方向和 claim 相反。
这类例子说明，Agent 的问题不是没有引用，而是会用相关论文包装一个过强甚至方向错误的结论。

## 25. Repair 的本质

这页是 refchecker repair 的关键解释：repair 不是错误消除，而是错误类型漂移。
20 个配对 claim 中，有 7 个 repair 后错误类型改变。有些从 contradiction 变成 overclaim，有些从 mis-citation 变成 overclaim。
这说明 Agent 在改写时缺乏对原文证据的深入理解，可能只是换一种更像学术写法的错误。

## 26. refchecker 归因总结

总结来说，refchecker 解决引用真实性，不解决引用支撑性。
repair 对 Agent 熟悉的 CS topic 可能有一点帮助，但对高专业度领域，比如 C3 生化任务，几乎无效。
最致命的盲区是 unsupported claim，因为它不是元数据错误，而是证据语义不充分。

## 27. Memory 错误总数

Memory 实验中，我们看 P1 和 P2 两轮。在 memory on 条件下，总体错误从 22 到 16，下降约 27%。
按 case 看，C1 错误数最低，C3 最高且稳定，C5 差异最大。
这说明 memory 有一定效果，但效果并不均匀，强依赖 case 类型。

## 28. Memory 错误类型图

这页展示 memory 条件下不同错误类型的分布。
重点是看 memory 减少了部分重复性错误，但没有解决所有问题。
尤其 unsupported claim 仍集中在 C3，说明 memory 无法弥补专业领域语义判断能力不足。

## 29. Memory 错误类型分析

Overclaim 在两个 run 中分布不稳定，尤其 C5 差异明显。
Unsupported claim 全集中在 C3，说明高专业领域仍是系统盲区。
比较好的现象是 contradiction 清零，说明 memory 至少帮助 Agent 避免最严重的“和原文对着干”的错误。

## 30. Memory vs Refchecker

这页是两个机制的对比。refchecker repair 总错误 40 到 40，没有减少，只是错误类型漂移。
Memory 条件下总错误 22 到 16，有实际下降。
我们的解释是：refchecker 是工具级元数据核查，memory 是经验级提醒，能减少一部分重复犯错。

## 31. Memory 归因

Memory 的效果主要出现在 C1、C2 这些主流 CS 或相对熟悉的领域。
对于 C3，unsupported claim 仍然 6/6 集中在那里，说明 memory 不能替代领域 expertise。
C5 差异大，说明 memory 效果不稳定，可能和该主题论文分布广、检索路径变化有关。

## 32. Side experiment：Action Memory 小实验

这里是一个辅助实验，不和正式 M1 结果混算。它用的是早期 action-memory 架构：`action_memory.jsonl` 存全部动作经验，`retrieve.py` 用 BM25 / summary_bm25 检索。
实验对比 run1 无记忆和 run2 有 run1 完整记忆：39 条 claim 中，错误从 11 个降到 2 个，错误率从 28.2% 到 5.1%，相对下降 82%。
最有价值的是有 3 条可追踪因果链：run1 审计发现错误并写入 error 字段，run2 检索命中 error 行，然后 Agent 明确修改 claim。
但也要诚实说明限制：这个实验有人工复审和审计威慑效应，而且 BM25 词袋检索无法解决 web_fetch 截断导致的全文细节缺失。

## 33. Side experiment：可追踪改善案例

这页给具体例子。第一个是 C1：run1 把 SWE-bench Verified 和原版 SWE-bench 的分数直接比较，run2 看到 error 后明确区分两个 benchmark 版本。
第二个是 C2：run1 把线性增长证明归给 [D]，但实际来自 Dohmatob et al.，run2 改成“[D] 提供因果框架，[F] 扩展 accumulate 场景”。
第三个是 C3：run1 把 challenged by 写成“系统性失败”，run2 降级为 struggle / 困难。
最后强调残余失败：C3 run2 仍有两个 overclaim，原因是细节来自全文记忆但 captured abstract 不包含，说明 memory 检索不能替代完整 source grounding。

## 34. 初步经验

这里可以作为 takeaway。科研 Agent 的引用问题不是“有没有引用”，而是“引用是否真的支撑结论”。
工具链本身必须先验证，否则基础设施噪声会污染实验结论。
refchecker 对元数据有帮助，但 claim support 需要 source-grounded 判断。memory 有帮助，但必须严格控制写入来源和运行顺序。

## 35. 一句话总结

最后总结：我们把一个模糊的问题，也就是“科研 Agent 会不会用看似可靠的引用支撑不可靠结论”，转化成了一个可复现、可标注、可消融的实验流程。
这个项目的价值不只在于当前数字，而在于建立了一套能继续扩展的评测框架。

## 2-3 分钟压缩版

如果时间很短，可以这样讲：

我们研究的是 OpenClaw 科研 Agent 的引用一致性问题。具体来说，Agent 生成的报告可能有引用，但引用并不一定真的支撑结论。我们没有修改 Agent 内部代码，而是从外部构造了一个可复现实验框架：五个科研主题、标准化 CPS 引用格式、固定四段输出 marker、arxiv MCP 文献获取、refchecker 元数据核查，以及 memory 条件下的 repair log 写回。

我们的第一个发现是，工具能力必须先预实验。arxiv MCP 能帮助找到真实论文和元数据，但不保证选到最贴题论文；refchecker 能核查论文真实性，但不能判断 claim support。因此，citation verification 不等于 claim verification。

在 refchecker repair 预实验里，总错误数从 40 到 40，没有下降。更细看发现，repair 经常只是错误类型漂移，比如 overclaim 变成 mis-citation，或者 contradiction 变成 overclaim。原因是 refchecker 只能给元数据层面的信号，Agent 仍然缺乏对原文证据的深入理解。

在 memory 主实验里，我们只把 `REFCHECKER_REPAIR_LOG` 的结构化 JSONL 写入 `active_memory.jsonl`，每次最多检索 top-6 条作为 procedural caution 注入 prompt。memory 不作为证据，也不写完整报告或人工标注。结果上，memory 条件下错误数从 22 降到 16，约 27%，说明它能减少一部分重复性错误，尤其在 C1、C2 这种主流 CS topic 上更明显。但 C3 的 unsupported claim 仍然集中出现，说明 memory 不能替代领域专业判断。

所以我们的结论是：OpenClaw 科研 Agent 的引用问题主要不是“没有引用”，而是“相关引用不等于充分支持”。refchecker 和 memory 都有价值，但它们解决的是不同层面的问题。最终要提高科研报告可靠性，还需要更强的 source-grounded claim verification。
