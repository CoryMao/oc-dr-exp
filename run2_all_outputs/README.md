# Action Memory 辅助实验输出包

这个目录保存 action-memory 辅助实验的一份 compact 输出包，包含 run1/run2 的科研报告、结构化 action memory JSONL，以及 memory retrieval/recall audit 报告。

它用于支持 `side_exp_md/action_memory_effectiveness_report.md` 中的复盘结论：当上一轮被人工审计过的引用错误能够被后续任务检索并注入上下文时，Agent 更容易避免重复性的引用错误。

## 文件结构

| 路径 | 内容 |
| --- | --- |
| `research_note_*_run1.md` | run1 生成的科研报告。 |
| `research_note_*_run2.md` | run2 在 action-memory 辅助下生成的科研报告。 |
| `action_memory/action_memory.jsonl` | action-level memory 记录，共 195 行。 |
| `action_memory/recall_audit_run1.md` | run1 后的 memory/recall 审计报告。 |
| `action_memory/recall_audit_run2*.md` | run2 的整体与分 case recall audit 报告。 |

## 覆盖范围

本目录覆盖 5 个研究主题：

- `tool_agents_vs_prompting`
- `model_collapse`
- `binding_affinity`
- `mllm_vision`
- `coding_agents`

`action_memory.jsonl` 中共有 195 条记录，主要 action 类型包括 `make_claim`、`fetch_paper`、`search_papers`、`extract_claim` 和 `other`。其中 claim generation 相关记录约 67 条，人工审计标出的错误类型包括 `Overclaim`、`Unsupported` 和 `Mis-citation`。

## 字段说明

`action_memory.jsonl` 每行是一条 JSON 记录，常见字段包括：

- `case_id`：实验 case 和 run 标识。
- `step`：该 case 内的 action 序号。
- `action_type`：动作类型，例如 `fetch_paper` 或 `make_claim`。
- `target`：当前动作目标。
- `success`：动作是否成功。
- `outcome`：动作结果或生成的 claim。
- `summary_en`、`keywords`：用于 BM25 / `summary_bm25` 检索的英文摘要和关键词。
- `is_claim_generation`：是否属于 claim 生成动作。
- `citation_error`、`error_type`、`error_reason`：引用错误审计字段。
- `timestamp`：记录写入时间。

其中 `error_type` 和 `error_reason` 是人工核查后手动填写的审计字段，不是 Agent 自动判断结果。

## 与正式主实验的关系

这个目录不是正式 `runs/main_memory/M1_memory_on/` 主实验结果，也不参与正式错误率统计。正式主实验使用 `evaluation/main_experiments/scripts/retrieve_memory_context.py` 对 normalized `REFCHECKER_REPAIR_LOG` rows 做 TF-IDF-like lexical retrieval。

本目录属于 action-memory side experiment，使用较早期的 `scripts/` 工具链和 BM25 / `summary_bm25` 检索，用来展示“细粒度行为记忆 + 人工审计错误字段”这一设计方向的效果和局限。
