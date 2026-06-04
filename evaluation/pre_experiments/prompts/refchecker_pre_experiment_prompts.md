# mcp-refchecker 预实验 Prompt

目的：测试 `mcp-refchecker` 是否能提高事后发现“引用与结论不一致”问题的能力。

运行说明：

- 被检查的 report 必须已经生成。
- 本 prompt 只做事后核查，不允许修改、重写或润色原 report。
- 每批 report 在 `no_refchecker` 和 `refchecker` 两个条件下分别检查。
- 每个条件运行 3 批：`R1`、`R2`、`R3`。
- 工具开关由 OpenClaw/workspace 配置控制，不依赖 prompt 约束。
- 输出填入 `evaluation/pre_experiments/refchecker_records.csv`。
- 以下字段由人工标注，检查 Agent 必须留空：`human_error_exists`、`human_error_type`、`human_judgment_note`。

允许的 `checker_error_type`：

- `none`
- `unsupported_claim`
- `overclaim`
- `mis_citation`
- `contradiction`
- `uncertain`

## Template: no_refchecker

```text
你现在不是继续完成原任务，也不是重写报告。你是一名事后检查员，需要检查一份已经生成的科研报告中是否存在“引用与结论不一致”的问题。

你需要检查的对象包括：

1. 已生成的 report
2. report 中引用的来源材料
3. report 中每条带引用的结论或 claim

你的目标不是改写答案，而是判断每条 claim 是否被它标注的引用材料充分支持。

## 硬性规则

1. 不要修改、重写、润色或补全原 report。
2. 只使用下面提供的 report 和来源材料进行人工式自检。
3. 不要写入 memory。
4. 如果某条 claim 或引用无法确认，不要猜测，标记为 `uncertain`。

---

## Report

{report_text}

---

## 来源材料

{source_materials}

---

## 错误类型定义

- `none`：引用材料能够支持该 claim，且支持强度与 claim 表述一致。
- `unsupported_claim`：claim 没有引用，或被引用材料不能支持该 claim。
- `overclaim`：被引用材料只支持较弱结论，但 report 写成了更强结论。
- `mis_citation`：被引用材料与主题相关，但不能支持该具体 claim。
- `contradiction`：被引用材料与 claim 相矛盾。
- `uncertain`：根据现有材料无法判断。

---

## 输出要求

只输出 JSONL，不要添加额外解释。

每行对应一条被检查的 claim。每个 JSON 对象必须包含以下字段：

{"report_id":"{report_id}","case_id":"{case_id}","run_id":"{run_id}","claim_id":"claim_01","checker_condition":"no_refchecker","human_error_exists":"","human_error_type":"","checker_flagged":"yes_or_no","checker_error_type":"none_or_error_type","checker_explanation":"用一句话说明 claim 与引用材料的对应关系","human_judgment_note":""}

字段规则：

- `claim_id` 从 `claim_01` 开始顺序编号。
- `checker_condition` 固定填写 `no_refchecker`。
- 如果 `checker_error_type` 为 `none`，`checker_flagged` 填写 `no`。
- 如果 `checker_error_type` 不是 `none`，`checker_flagged` 填写 `yes`。
- `human_error_exists` 留空。
- `human_error_type` 留空。
- `human_judgment_note` 留空。
```

## Template: refchecker

```text
你现在不是继续完成原任务，也不是重写报告。你是一名事后检查员，需要检查一份已经生成的科研报告中是否存在“引用与结论不一致”的问题。

你需要检查的对象包括：

1. 已生成的 report
2. report 中引用的来源材料
3. report 中每条带引用的结论或 claim

你的目标不是改写答案，而是使用 mcp-refchecker 辅助判断每条 claim 是否被它标注的引用材料充分支持。

## 硬性规则

1. 不要修改、重写、润色或补全原 report。
2. 使用可用的引用核查工具核查已有 claim-citation pair。
3. 引用核查工具只能用于核查，不得用于生成新 claim 或改写结论。
4. 只使用下面提供的 report 和来源材料。
5. 不要写入 memory。
6. 如果引用核查工具无法解析、无法访问或无法确认某条引用，不要猜测，标记为 `uncertain`。

---

## Report

{report_text}

---

## 来源材料

{source_materials}

---

## 错误类型定义

- `none`：引用材料能够支持该 claim，且支持强度与 claim 表述一致。
- `unsupported_claim`：claim 没有引用，或被引用材料不能支持该 claim。
- `overclaim`：被引用材料只支持较弱结论，但 report 写成了更强结论。
- `mis_citation`：被引用材料与主题相关，但不能支持该具体 claim。
- `contradiction`：被引用材料与 claim 相矛盾。
- `uncertain`：根据现有材料无法判断。

---

## 输出要求

只输出 JSONL，不要添加额外解释。

每行对应一条被检查的 claim。每个 JSON 对象必须包含以下字段：

{"report_id":"{report_id}","case_id":"{case_id}","run_id":"{run_id}","claim_id":"claim_01","checker_condition":"refchecker","human_error_exists":"","human_error_type":"","checker_flagged":"yes_or_no","checker_error_type":"none_or_error_type","checker_explanation":"用一句话说明核查结果与 claim 的关系","human_judgment_note":""}

字段规则：

- `claim_id` 从 `claim_01` 开始顺序编号。
- `checker_condition` 固定填写 `refchecker`。
- 如果 `checker_error_type` 为 `none`，`checker_flagged` 填写 `no`。
- 如果 `checker_error_type` 不是 `none`，`checker_flagged` 填写 `yes`。
- `human_error_exists` 留空。
- `human_error_type` 留空。
- `human_judgment_note` 留空。
```
