# 答辩 QA Pairs：OpenClaw 引用一致性评测

## 一、研究问题与实验定义

### Q1. 你们说的“引用与结论不一致”到底怎么定义？

A: 我们以 claim-citation pair 为单位定义。报告中的一个结论如果绑定了某个引用位置，但该位置不能充分支持这个结论，就算不一致。常见情况包括：引用材料只支持更弱结论、引用讨论的是不同任务或不同条件、结论超出原文范围、引用位置错误，或者引用材料与结论方向相反。

### Q2. 这和 hallucinated citation 有什么区别？

A: Hallucinated citation 主要是引用不存在或元数据虚构；我们关注的是更隐蔽的问题：引用可以是真实论文、标题作者年份也正确，但该引用并不能支撑 claim。也就是说，真实引用不等于有效支撑。

### Q3. 为什么这个问题重要？

A: 科研 Agent 的报告通常看起来很可信，因为它有文献和 citation。但如果 citation 只是“看起来相关”，不真正支持结论，用户会被误导，而且这种错误比无引用更难发现。我们希望把这种隐蔽风险变成可复现、可统计的评测对象。

### Q4. 你们的评测单位是什么？

A: 评测单位是 claim-citation pair。我们先让 Agent 输出结构化报告，再从报告中抽取每条 claim 和对应 citation scope，判断该 citation scope 是否支撑 claim。

### Q5. 为什么选五个 case？

A: 五个 case 覆盖不同主题和证据形态：coding agent、synthetic data/model collapse、protein-ligand docking、多模态认知 benchmark、AI coding productivity。这样可以避免只在一个模型熟悉的 CS topic 上测试，也能观察领域专业度对错误类型的影响。

## 二、系统架构与 OpenClaw 配置

### Q6. 被测系统具体是什么？

A: 被测系统是 OpenClaw + DeepSeek v4 Pro + skills + MCP 的科研 Agent。固定工具包括 PDF skill、citation-standard skill、arxiv MCP、mcp-refchecker、Brave web search。memory 条件下额外使用我们实现的 JSONL memory 检索注入机制。

### Q7. 你们有没有改 Agent 内部代码？

A: 没有。我们没有修改 OpenClaw 或模型内部逻辑。所有控制都通过 prompt、skills、MCP 配置、profile/workspace 隔离、外部运行脚本、输出解析和 memory JSONL 实现。

### Q8. 为什么使用 DeepSeek v4 Pro？

A: 它是实验计划中固定的基模。这里重点不是比较不同基模，而是在固定基模和固定工具栈下，系统性观察科研报告生成中的引用支撑问题。不同基模可以作为后续 ablation。

### Q9. 为什么要固定 planning，不做 plan 变量？

A: 时间成本和变量控制。我们最终把 planning 固定为 OpenClaw 默认行为，把主变量集中到工具和 memory 上。这样实验更容易复现，也减少解释时的混杂因素。

### Q10. 为什么 web search 要固定为 Brave？

A: 之前 profile 配置中 web search provider 有漂移风险。固定 Brave 可以减少不同 profile 间工具差异，让失败更容易归因，不会把 provider 变化误认为模型能力差异。

## 三、citation-standard 与输出格式

### Q11. citation-standard skill 解决什么问题？

A: 它解决引用格式不可解析的问题。自由文本引用如“见 introduction”或“第 5 页附近”很难稳定标注。citation-standard 要求使用 CPS 形式，例如 `[A] §4.1::¶2`，从而让每条 claim 的证据位置可追踪、可解析。

### Q12. CPS 的核心规则是什么？

A: CPS 包括文献标签、scope 和 element。例如 `[A] §4.1::¶2` 表示文献 A 第 4.1 节第 2 段；也可以是 `::T2` 表格、`::F4` 图片等。多个位置用分号分隔，每个位置都必须带完整 scope。

### Q13. 为什么要求四段 marker？

A: 四段 marker 让输出可程序化拆分：`ORIGINAL_REPORT` 是原始报告，`REFCHECKER_REPAIR_LOG` 是结构化核查记录，`REPAIRED_REPORT` 是修复后报告，`RUN_SUMMARY` 是运行摘要。没有 marker，后续抽取和统计会不稳定。

### Q14. 如果 Agent 输出格式不合规怎么办？

A: run log 会标记 `markers_ok=no`，这类 run 不会写入 memory，也不应进入正式统计，或者需要用新 session key 重试。这样避免格式失败污染 memory 和结果。

## 四、arxiv MCP 预实验

### Q15. arxiv MCP 预实验测试的是什么？

A: 测试 Agent 是否能自主找到合适的 [D][E][F] 论文。我们比较 arxiv on/off，记录论文是否真实、是否相关、是否全文可得、是否重复或偏题。

### Q16. 为什么 arxiv MCP 没显著提高贴合度？

A: 因为 arxiv MCP 主要提高 paper existence、metadata 和 access，不是 relevance optimizer。它能帮助找到真实论文，但选择“最贴题论文”仍取决于 Agent 的检索策略和任务理解。

### Q17. 那为什么主实验还要固定开启 arxiv MCP？

A: 因为主实验需要稳定获取真实论文和元数据。即使它不保证 relevance 最优，它仍然降低 hallucinated citation 和元数据错误风险。我们把它作为固定基础设施，而不是主效果变量。

### Q18. Case 5 为什么表现特殊？

A: AI coding tools 主题空间很散，可能涉及 productivity、adoption、SWE-Bench、workflow、developer perception 等多个方向。Agent 容易选到相关但不直接支撑核心问题的论文，因此贴合度波动更大。

### Q18a. arxiv MCP 在我们的系统里具体怎么工作？

A: OpenClaw 通过 MCP stdio 启动 arxiv server，Agent 可以调用 arxiv 相关工具完成三类动作：搜索论文、获取 abstract/metadata、下载或读取论文全文。上游 arxiv MCP 通常会访问 `export.arxiv.org` 的 Atom API 做 search，并通过 arXiv ID 获取 abstract、PDF 或缓存后的文本。我们的 profile 会把 arxiv MCP 的存储目录固定到对应 workspace 下，例如 `workspace/arxiv_mcp_papers`，避免不同实验 profile 混用缓存。

### Q18b. 为什么还写了 `openclaw_arxiv_mcp_safe.py` safe wrapper？

A: 因为实际运行中 arXiv 工具链有两个不稳定点：第一，`export.arxiv.org/api/query` 容易 429、timeout 或被代理/DNS 影响；第二，下载后上游 MCP 可能做额外 indexing，导致长 run 不稳定。safe wrapper 保留原 MCP tool names，但改了底层行为：搜索时设置短 timeout，失败时返回 warning 而不是挂死；下载 PDF 时直接走 `https://arxiv.org/pdf/<id>`，再用 `pdftotext` 转文本；读全文时对返回内容做字符上限截断，避免一次把超长论文塞进工具响应。

### Q18c. arxiv MCP 和普通 web search 的区别是什么？

A: web search 适合广泛找网页和候选论文，但返回结果可能是网页片段、博客或不稳定 URL。arxiv MCP 更像结构化学术检索和读取接口：输入 query 或 arXiv ID，返回论文 metadata、abstract、PDF URL 或文本内容。我们的实验里两者都开，但作用不同：Brave web search 提供广义检索，arxiv MCP 提供更结构化的 arXiv 论文访问。

### Q18d. arxiv MCP 为什么不能保证选出的论文最贴题？

A: MCP 只是工具，不是文献选择策略本身。它能把搜索和下载做得更可靠，但 query 怎么写、哪些结果被认为是核心文献、是否覆盖任务中的因果链和证据需求，仍然由 Agent 决定。所以我们看到 arxiv on 可以提高真实论文和元数据可靠性，但不必然提高 topic relevance。

## 五、refchecker repair

### Q19. refchecker 能做什么？

A: 它主要做 citation metadata verification：检查论文是否存在，标题、作者、年份、DOI/arXiv ID 是否匹配。它对引用真实性和元数据一致性有帮助。

### Q19a. mcp-refchecker 在我们的系统里具体怎么工作？

A: mcp-refchecker 也是通过 MCP stdio 接入 OpenClaw 的工具服务器。Agent 在 repair 阶段把某条参考文献的标题、作者、年份、DOI/arXiv ID 等信息传给 refchecker 工具；refchecker 再去外部学术出版物数据库或索引中交叉核验，返回该 citation 是否能匹配到真实出版物，以及匹配到的标准 metadata。我们在输出中把这些核查结果记录进 `REFCHECKER_REPAIR_LOG`。

### Q19b. refchecker 的输入输出大概是什么？

A: 输入通常是 reference-level metadata，例如 title、authors、year、venue、DOI、arXiv ID，或者一个待验证 citation string。输出不是“这个 claim 是否正确”，而是 citation metadata 层面的结果：是否找到匹配记录、标准标题/作者/年份是什么、identifier 是否一致、是否存在作者或年份 mismatch。Agent 再根据这些结果决定是否修正 reference list 或 citation metadata。

### Q19c. 为什么我们还写了 `openclaw_refchecker_mcp_safe.py`？

A: OpenClaw 用 stdio 和 MCP server 通信，stdout 必须只包含 JSON-RPC 消息。如果 MCP server 或底层 FastMCP 把 INFO log 打到 stdout，OpenClaw 可能会把它当成协议污染，报 `MCP error -32000: Connection closed`。`openclaw_refchecker_mcp_safe.py` 不改变 refchecker 的工具行为，只是把日志强制导向 stderr，并压低 MCP request log 级别，保证 stdio 协议干净。

### Q20. refchecker 不能做什么？

A: 它不能直接判断 claim 是否被某个段落或表格充分支持，也不能判断领域专业证据强度。因此 citation verification 不等于 claim verification。

### Q20a. 为什么 refchecker 查到 citation 正确，claim 仍然可能错？

A: 因为这两个问题层级不同。refchecker 只能说明“这篇论文/这个 DOI/这个 arXiv ID 是否真实，metadata 是否匹配”；claim verification 要判断“报告里的这个具体结论是否被论文里的这个段落、表格或实验结果支持”。例如论文真实存在且题目完全正确，但报告 claim 把论文中的局部 benchmark 结果推广成普遍规律，这就是 overclaim，refchecker 不会自动发现。

### Q20b. refchecker 和 citation-standard 的关系是什么？

A: citation-standard 解决“引用位置怎么写得可解析”，refchecker 解决“引用的文献元数据是否真实”。二者互补但都不等于 claim support 判定。即使 `[A] §4.1::¶2` 格式正确、[A] 的标题作者年份也正确，我们仍然要检查 §4.1 第 2 段是否真的支持该 claim。

### Q21. 为什么 refchecker repair 总错误数没有下降？

A: 因为很多错误不是元数据错误，而是 unsupported claim 或 overclaim。refchecker 能修 metadata，但 Agent 在改写时仍然可能误解原文证据，于是错误只是从一种类型变成另一种类型。

### Q22. 什么叫“错误类型漂移”？

A: 指 repair 后 claim 仍然错误，但错误类型变了。例如原来是 overclaim，repair 后变成 mis-citation；或者 contradiction 变成 overclaim。总错误没有减少，只是换了一种错法。

### Q23. 为什么 C1 有改善，而 C3 没有？

A: C1 是主流 CS/coding agent topic，模型先验知识更强，refchecker 提示后更容易合理改写。C3 是蛋白-配体 docking，涉及专业定量 claim，模型需要更强领域知识才能判断证据是否充分，所以 repair 几乎无效。

### Q24. 为什么说 unsupported claim 是最致命盲区？

A: 因为 unsupported claim 的引用常常是真实且元数据正确的，只是证据不支持结论。工具层面的 citation check 很难发现它，但它直接影响科研报告的可信度。

## 六、Memory 机制技术细节

### Q25. 你们的 memory 是 OpenClaw 内置 memory 吗？

A: 不是。我们实际使用的是外部显式 JSONL memory 机制。共享文件是 `runs/main_memory/M1_memory_on/_memory/active_memory.jsonl`，由我们的脚本负责 retrieve、prompt injection 和 write-back。

### Q26. memory 写入什么？

A: 只写入 `REFCHECKER_REPAIR_LOG` 中的结构化 JSONL 行，包括 `reference_metadata` 和 `claim_citation_pair`。字段包括 issue type、repair action、citation tag、summary、keywords 等。不写完整报告、不写人工标注、不写 chain-of-thought、不写 session history。

### Q27. memory 什么时候写入？

A: 每个 memory_on run 结束后，只有当四段 marker 完整、没有 timeout/API/MCP hard failure 时，才抽取 repair log 并 append 到 `active_memory.jsonl`。如果 markers 不完整，则跳过 write-back。

### Q28. memory 怎么 retrieve？是 BM25 还是 TF-IDF？

A: 正式主实验用的是 TF-IDF-like token scoring，不是 BM25。run 前调用 `retrieve_memory_context.py`，读取 `active_memory.jsonl`，用当前 case id、topic，以及 citation、metadata、support、overclaim、scope_error、refchecker、repair、CPS 等关键词组成 query，然后按词频、IDF 和长度归一化打分。

### Q29. 每次 retrieve 多少条？

A: 默认 `top_k=6`，也就是最多 6 条。这个值写在每个 run manifest 的 memory 配置里。P1_C1 因为 memory 为空，retrieve 0 条；后续通常取满 6 条。

### Q30. retrieve 的排序依据是什么？

A: 基础是 query token 与 memory record token 的词匹配，并做 idf 和长度归一化。额外 boost 包括：`issue_type != none` 加 1.5，`repair_action != none` 加 0.5，当前 case id 命中加 0.75。因此有错误、有修复动作、同 case 相关的记录更容易被选中。

### Q30a. 那仓库里的 BM25 memory 脚本是什么？

A: `scripts/retrieve.py` 是更早的 action-memory 草案，支持 `bm25`、`summary_bm25`、`hybrid` 和 `tfidf`。正式 main memory MVP 为了保持实现简单、可复现、和 refchecker repair log 对齐，没有使用这套 BM25 脚本，而是使用 `evaluation/main_experiments/scripts/retrieve_memory_context.py`。

### Q31. memory 注入到哪里？

A: retrieve 结果写入 `memory_context.md`，再和 `prompt.base.md` 拼接成最终 `prompt.md`。Agent 看到的是 prompt 开头的 `MEMORY_CONTEXT` 区块。

### Q32. memory 会不会被 Agent 当成证据？

A: prompt 明确写了 memory 是 procedural caution，不是 scientific evidence，不能引用。所有科学 claim 仍必须由 [A]-[F] 源材料和 CPS 位置支持。

### Q33. 当前最终 memory 有多少条？

A: 当前最终 `active_memory.jsonl` 有 97 条记录。它来自成功写回的 runs；失败或 marker 不完整的 runs 不会写入。

### Q34. 为什么 retrieve log 里会有 retry 或旧记录？

A: `retrieve_log.jsonl` 是运行过程日志，保留了 retry 和调试历史。正式分析时不能直接全量使用 retrieve log，而要按最终 P1/P2 的 manifest 和 run log 过滤。

### Q35. memory 为什么只跑 P1/P2？

A: 时间成本和稳定性考虑。我们最终把主实验范围收敛为两轮：P1 提供初始经验，P2 测试经验是否被利用。P3 不进入最终主实验协议。

## 七、Memory 结果解释

### Q36. memory 的主要效果是什么？

A: 在 M1 memory_on 条件下，总错误从 22 降到 16，下降约 27%。这说明结构化 repair memory 能减少一部分重复犯错，尤其在 C1、C2 这种模型较熟悉的主题上更明显。

### Q37. memory 为什么比 refchecker repair 有效？

A: refchecker repair 主要提供当前 run 的元数据核查信号；memory 则把之前 run 的错误经验转化为 prompt caution，能让 Agent 在后续生成时提前避开类似错误。它减少的是重复犯错，而不是只做事后元数据修正。

### Q38. memory 为什么对 C3 无效？

A: C3 的主要错误是 unsupported claim，而且集中在专业定量结论上。memory 只能提醒“之前这种 claim 可能有支撑问题”，但不能替代蛋白-配体领域的专业判断，也不能自动验证定量实验条件是否匹配。

### Q39. contradiction 清零能说明什么？

A: 这说明 memory 对最严重的方向性错误可能有帮助。Agent 看到之前 repair log 中的警示后，更少生成与原文方向相反的 claim。但这不代表所有错误都解决了，unsupported claim 仍然存在。

### Q40. C5 两轮差异大怎么解释？

A: C5 主题本身论文分布广，涉及 developer productivity、SWE-Bench、adoption、workflow 等多个方向。不同检索路径会导致证据材料变化，从而让错误数波动更大。这也说明 memory 效果不稳定，需要更多 run 或 counterbalanced order 验证。

### Q40a. action-memory side experiment 和正式主实验有什么区别？

A: side experiment 用的是早期 action-memory 架构，`action_memory.jsonl` 记录更细粒度的 agent 动作，`retrieve.py` 使用 BM25 / `summary_bm25` 检索；正式主实验用的是 refchecker repair log 派生的 `active_memory.jsonl`，检索脚本是 `retrieve_memory_context.py`，打分是 TF-IDF-like lexical scoring。side experiment 不和正式 M1 结果混算，它只是补充说明：当错误审计结果能被后续检索命中时，Agent 确实会减少重复性引用错误。

### Q40b. side experiment 的结果是什么？

A: 在 run1 无记忆、run2 有 run1 完整记忆的设置下，39 条 claim 的错误从 11 个降到 2 个，错误率从 28.2% 降到 5.1%，相对下降 82%。其中有 3 条可追踪因果链：run1 审计写入 error 字段，run2 检索命中 error 行，然后 Agent 修改 claim。但这个结果也受人工复审和审计威慑影响，所以我们把它作为 side evidence，而不是正式主结论。

### Q40c. side experiment 里有哪些具体改善例子？

A: 三个最清晰的例子是：第一，C1 Step 8 中 run1 混用了 SWE-bench Verified 和原版 SWE-bench 的分数，run2 明确区分 benchmark 版本并说明不宜直接比较绝对值；第二，C2 Step 15 中 run1 把“测试误差线性增长”的数学证明错误归因给 [D]，run2 改为说明证明来自 Dohmatob et al.，而 [D] 只是提供因果框架；第三，C3 Step 9 中 run1 把原文的 `challenged by` 升级成“系统性失败”，run2 降级为 `struggle` / “困难”。这说明 memory 的价值主要在于把过去的错误转成后续生成前的提醒。

## 八、评测与统计

### Q41. 你们的错误分类有哪些？

A: 主要包括 unsupported claim、overclaim、mis-citation、contradiction 和 metadata error。unsupported claim 是证据不足；overclaim 是结论强于证据；mis-citation 是引用位置或对象不匹配；contradiction 是引用方向相反；metadata error 是作者标题年份 ID 等错误。

### Q42. 评测是人工还是 LLM？

A: 当前结果使用 citation_check 流水线：人工定义错误分类和 few-shot prompt，然后用 DeepSeek 作为 judge 批量判断。严格来说这不是最终人工金标，应该在答辩中承认它是可扩展的自动评测版本，后续可以用人工抽样复核。

### Q43. LLM-as-judge 会不会有偏差？

A: 会，所以我们把它作为当前阶段的统计工具，而不是绝对真值。我们通过固定 prompt、few-shot 示例、结构化输入和相同 judge 模型来提高一致性。最终更严谨的版本应该加入人工标注或双人标注一致性。

### Q44. 为什么不用准确率、召回率？

A: 如果没有人工 gold labels，很难计算真正的 precision/recall。当前我们更关注错误总数、错误类型分布、repair 前后变化，以及 memory P1/P2 的趋势。等人工标注完成后，可以再计算 detection precision/recall 或 inter-annotator agreement。

### Q45. 为什么 no-memory baseline 用 refchecker repair 预实验？

A: 时间成本限制下，我们没有重新跑 formal M0，而是使用已经完成的 `pre_refchecker_repair` 作为 practical no-memory baseline。它工具栈和输出格式接近主实验，但这个选择需要作为 limitation 说明。

### Q46. memory 实验固定 C1-C5 顺序会不会有偏差？

A: 会。固定顺序让实验更可复现，但会把 memory effect 和 case order 混在一起。我们在分析中同时看 within-pass trend 和 same-case P1/P2 trend，并把未 counterbalance 作为 limitation。

## 九、工程问题与复现

### Q47. 为什么不能并行跑？

A: 实际测试中 `JOBS=2` 会放大 arXiv、web search 和 DeepSeek API timeout，也会让 memory 写入顺序复杂化。memory_on 条件共享一个 `active_memory.jsonl`，所以必须 `JOBS=1` 顺序执行。

### Q48. arxiv MCP 的 `-32000` 是什么问题？

A: MCP server 手动握手可以正常，但 OpenClaw bundle-MCP 层偶发连接失败。我们用 safe wrapper、限速和 profile audit 降低影响，并把它记录为基础设施限制。

### Q49. 代理设置为什么重要？

A: arxiv.org、export.arxiv.org、Brave search 和 web fetch 走的网络路径不同。错误代理或 fake-IP 会导致 DNS 污染、timeout 或无法下载 PDF。实验前必须固定 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY`。

### Q50. 如何保证 profile 不互相污染？

A: 预实验使用独立 profile 和 workspace；主 memory 条件使用共享 memory 文件但每个 case 新 session key。profile audit 记录 MCP、skills、workspace、web search provider、memory/search settings。

### Q51. 如何保证 memory 不污染科学证据？

A: 第一，memory 不包含原文材料和完整报告，只包含 repair log 摘要。第二，prompt 明确禁止引用 memory。第三，所有科学结论仍要求 [A]-[F] 和 CPS location 支持。第四，memory 只用于 procedural caution。

### Q52. 为什么 presentation/main_memory 不上传？

A: 它包含大量中间输出和论文 PDF，体积很大，也不是理解 PPT 的必要材料。最终仓库保留 PPT、图表和源码即可；大文件可以本地保留或放外部存储。

## 十、威胁有效性与改进方向

### Q53. 你们实验最大的 limitation 是什么？

A: 主要有四点：第一，当前 judge 是 LLM-as-judge，不是完全人工金标；第二，memory 顺序没有 counterbalance；第三，case 数和 run 数有限；第四，工具链本身有网络和 MCP 稳定性问题。我们通过日志、profile audit 和固定配置尽量降低影响。

### Q54. 如果要进一步严谨，你们会怎么做？

A: 增加人工双标和一致性检验；加入 counterbalanced case order；扩大 run 数；区分 active retrieval、passive memory 和 no memory；增加基模 ablation；把 source-grounded verifier 作为独立组件，而不是只依赖 refchecker。

### Q55. 你们怎么证明错误来自脚手架还是基模？

A: 当前设计还不能完全分离。可以做 ablation：同一 prompt 下比较 base model without tools、OpenClaw with tools、OpenClaw without memory、OpenClaw with memory；也可以换基模。如果同一基模在脚手架中错误增加，可能是 scaffold/tool interaction；如果所有设置都错，可能是基模或任务本身困难。

### Q56. refchecker 无效是否意味着它没价值？

A: 不是。它对元数据核查有价值，可以减少 hallucinated or wrong citations。但它不能解决 claim support。我们的结论是它应被定位为 citation metadata checker，而不是 claim verifier。

### Q57. memory 有效是否意味着应该长期打开？

A: 不一定。我们的 memory 是受控的结构化 repair log，效果在 C1/C2 更好，在 C3 无效，C5 不稳定。实际系统中如果 memory 写入范围更宽，可能引入污染。因此 memory 应该有严格 schema、来源控制和过期/过滤机制。

### Q58. 为什么不用 embedding retrieval？

A: MVP 优先可解释和可复现。TF-IDF-like 词匹配能清楚说明为什么某条 memory 被选中，并且不引入额外 embedding 模型变量。后续可以把 embedding retrieval 作为增强版本比较。

### Q59. top-k=6 为什么合理？

A: top-k=6 是折中：足够覆盖多个历史错误类型，但不会让 prompt 被 memory 淹没。再多会增加上下文噪声，也可能让 Agent 过度依赖历史案例。这个值不是理论最优，后续可以做 top-k ablation。

### Q60. 你们最终最重要的结论是什么？

A: 科研 Agent 的引用风险核心不是“有没有引用”，而是“引用是否充分支持结论”。refchecker 能解决引用真实性的一部分问题，但不能解决语义支撑。结构化 memory 能减少部分重复错误，但不能替代 source-grounded claim verification 和领域知识。

## 十一、简短答辩话术

### 如果老师质疑“这个项目是不是只是 prompt engineering？”

A: 我会说：prompt 是实验控制的一部分，但项目重点不是调 prompt，而是建立可复现评测框架。我们控制了 profile、skills、MCP、workspace、session key、输出 contract、citation syntax、run logs 和 memory writeback。核心贡献是把 citation-claim mismatch 变成可抽取、可标注、可统计的实验对象。

### 如果老师质疑“结果是否可靠？”

A: 当前结果是自动评测版本，可靠性来自固定 judge prompt、结构化 claim-citation 输入和完整日志，但我们承认还不是最终人工金标。更严谨版本会加入人工双标、一致性统计和更大 run 数。现阶段结果主要用于发现 failure pattern 和验证评测框架可运行。

### 如果老师问“最意外的发现是什么？”

A: 最意外的是 refchecker repair 没有降低总错误数，而只是错误类型漂移。它能修元数据，但 Agent 可能把 claim 改成另一种不被支持的说法。这说明 citation verification 和 claim verification 必须分开设计。

### 如果老师问“memory 真的是学到了吗？”

A: 我会谨慎说：我们不能证明模型内部真正学习了，只能说结构化历史 repair log 被检索并注入后，后续输出中的部分错误减少了。这个更准确地叫 experience-conditioned generation，而不是参数层面的 learning。

### 如果老师问“下一步最应该做什么？”

A: 下一步是做人工标注和更强的 source-grounded verifier。尤其要针对 unsupported claim，因为这是 refchecker 和当前 memory 都无法稳定解决的核心盲区。
