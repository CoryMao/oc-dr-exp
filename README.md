# OpenClaw DeepResearch 引用一致性评测

本仓库是一个可复现的实验交付包，用于测试 OpenClaw 搭建的科研 Agent 在生成科研报告时是否存在“引用与结论不一致”的问题。

这里的“引用与结论不一致”指：Agent 给出的结论看起来有引用或材料支持，但实际检查后发现引用材料并不能充分支持该结论，甚至与结论相矛盾。本项目不修改 OpenClaw 内部代码，而是通过 prompt、skill、MCP/profile 配置、运行脚本、结构化日志、引用格式校验、refchecker repair log 和外部 judge 脚本控制实验。

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `citation-standard/` | OpenClaw skill：要求报告输出标准化 CPS 引用格式，并提供语法 validator。 |
| `case paper/` | 小规模、已跟踪的测试论文材料。未来新增的大型论文包默认忽略。 |
| `evaluation/pre_experiments/` | arXiv MCP 与 refchecker repair 预实验的 prompts、profile setup 脚本、run manifests 和记录表。 |
| `evaluation/main_experiments/` | 正式 memory 实验脚本、manifest、输出清单和 action-length 图表。 |
| `evaluation/judge/` | claim-citation pair 抽取、LLM judge batch 构造、聚合统计和结果图表。 |
| `runs/pre_arxiv/` | 已完成的 arXiv MCP 预实验运行产物。 |
| `runs/pre_refchecker_repair/` | 已完成的 refchecker repair 预实验产物；在最终展示中作为 practical no-memory baseline。 |
| `runs/main_memory/M1_memory_on/` | 正式 memory-on 主实验 P1/P2 运行产物，包括 per-run 日志和共享 memory JSONL。 |
| `scripts/` | action-memory 辅助实验工具链：append/retrieve/pre-action hook/case-runner 等工具。 |
| `side_exp_md/` | action-memory 辅助实验复盘报告。 |
| `presentation/` | 最终 Beamer slides、图表、讲稿和答辩 QA。 |
| `docs/` | 实验设计说明和过程性 rationale。 |

## 环境要求

本地需要：

- 已安装 OpenClaw。
- Python 3.10+。
- `bash`、`git`、`rg`。
- 如需重新编译展示材料，需要 `xelatex` 和 `pdfinfo`。
- OpenClaw 运行或 LLM judge 需要 DeepSeek-compatible API key。
- 实验 profile 中需要配置 Brave search provider。

推荐环境变量：

```bash
# DeepSeek key，用于 OpenClaw 运行和可选的 LLM judge。
# 真实 key 只放在本机 shell/profile 中，不要提交到仓库。
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"

# 本实验作者机器上使用的本地代理配置。
# 127.0.0.1:7897 是本机 Clash HTTP/HTTPS proxy endpoint。
export HTTPS_PROXY="http://127.0.0.1:7897"
export HTTP_PROXY="http://127.0.0.1:7897"

# arXiv 和本地 OpenClaw/MCP 流量不走代理。
# 如果你的代理导致 DeepSeek CONNECT timeout，可在本机把 api.deepseek.com 加入这里。
export NO_PROXY="arxiv.org,export.arxiv.org,localhost,127.0.0.1"
```

OpenClaw 运行脚本要求提供 `OPENCLAW_RUN_CMD`。该命令需要读取 `$PROMPT_FILE`，并将 agent 输出写到 stdout：

```bash
# runner 会设置 OPENCLAW_PROFILE、SESSION_KEY、THINKING_LEVEL 和 PROMPT_FILE。
export OPENCLAW_RUN_CMD='openclaw --profile "$OPENCLAW_PROFILE" agent --local --timeout 2400 --thinking "$THINKING_LEVEL" --session-key "$SESSION_KEY" --message "$(cat "$PROMPT_FILE")"'
```

默认使用 `JOBS=1`。开发过程中发现并行运行会放大 web search、MCP 和 DeepSeek timeout 等基础设施噪声。

## 复现入口

### 1. 校验引用格式

```bash
python3 citation-standard/scripts/validate.py <report.md>
```

期望的 CPS 引用格式见 `citation-standard/references/cps-spec.md`。

### 2. arXiv MCP 预实验

```bash
bash evaluation/pre_experiments/scripts/prepare_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/preflight_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/setup_arxiv_profiles.sh
JOBS=1 SKIP_EXISTING=1 bash evaluation/pre_experiments/scripts/run_arxiv_runs.sh
bash evaluation/pre_experiments/scripts/collect_arxiv_outputs.sh
```

已完成的运行产物位于 `runs/pre_arxiv/`。

### 3. Refchecker Repair 预实验

```bash
bash evaluation/pre_experiments/scripts/prepare_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/preflight_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/setup_refchecker_repair_profiles.sh
JOBS=1 SKIP_EXISTING=1 bash evaluation/pre_experiments/scripts/run_refchecker_repair_runs.sh
bash evaluation/pre_experiments/scripts/collect_refchecker_repair_outputs.sh
```

已完成的运行产物位于 `runs/pre_refchecker_repair/`。这些输出在最终展示中作为 practical no-memory baseline。

### 4. 正式 Memory 实验

最终项目范围只采用 `M1_memory_on`，并运行两个顺序 pass：

```text
(C1 -> C2 -> C3 -> C4 -> C5) x 2 passes
```

运行或恢复：

```bash
bash evaluation/main_experiments/scripts/prepare_main_memory_runs.sh
bash evaluation/main_experiments/scripts/preflight_main_memory_runs.sh
bash evaluation/main_experiments/scripts/setup_main_memory_profiles.sh

JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh

# 如需从中间继续：
MAIN_MEMORY_START_AT=P2_C3 JOBS=1 SKIP_EXISTING=1 bash evaluation/main_experiments/scripts/run_main_memory_runs.sh
```

memory-on 条件共享同一个 memory 文件，因此 runner 强制串行执行：

```text
runs/main_memory/M1_memory_on/_memory/active_memory.jsonl
```

### 5. Judge Pipeline

构造 claim-citation 输入并聚合 LLM judge 结果：

```bash
python3 evaluation/judge/build_judge_inputs.py --help
python3 evaluation/judge/run_deepseek_judge.py --help
python3 evaluation/judge/aggregate_judgments.py --help
```

仓库包含已生成的图表和 claim-citation input batches，但不包含 API keys，也不提交不完整或空的 judge output 文件。

大型 pass-specific evidence cache `presentation/main_memory/` 不进入版本库。如需从 PDF 重新构造 judge snippets，可在本地用 `evaluation/judge/sync_presentation_papers.py` 重建。

### 6. 展示材料

```bash
cd presentation
xelatex -interaction=nonstopmode -halt-on-error openclaw_deepresearch_overview.tex
xelatex -interaction=nonstopmode -halt-on-error openclaw_deepresearch_overview.tex
```

提交前请删除 LaTeX build artifacts。

## 最终实验范围

- plan ablation 已取消；最终运行使用 OpenClaw 默认 planning。
- 由于时间成本限制，没有重新跑 formal no-memory M0；已完成的 `pre_refchecker_repair` 作为 practical no-memory baseline。
- 正式 main memory 使用从 `REFCHECKER_REPAIR_LOG` 派生的结构化 JSONL memory。它只作为 procedural caution 注入 prompt，不作为科学证据，也不能被引用。
- `side_exp_md/` 中的 side experiment 使用另一套 action-memory 设计，检索方法为 BM25 / `summary_bm25`。它只作为辅助证据，不与正式 M1 memory 结果混算。

## Action Memory 辅助实验

`scripts/` 包含较早期的 action-memory 工具链，用于辅助探索。它支持 append/retrieve workflow、pre-action retrieval hook、case-step runner，以及 BM25、`summary_bm25`、hybrid scoring、TF-IDF 等 lexical retrieval 方法。

这套工具链与正式 main-memory MVP 分离。正式主实验使用 `evaluation/main_experiments/scripts/retrieve_memory_context.py`，并在 normalized `REFCHECKER_REPAIR_LOG` rows 上做检索。本仓库不声称包含完整 action-memory 实验日志；`side_exp_md/` 是辅助复盘报告，不是正式主结果的可复现包。

在 `scripts/action_memory.jsonl` 中，`error_type` 和 `error_reason` 是人工核查后手动填写的审计字段，不是 agent 自动生成的判断信号。

## 复现说明

- 每个 OpenClaw run directory 都保存 `run_manifest.json`、`prompt.md`、`output.raw.txt`、`stderr.log`、`run.log`，并在可用时保存 profile audit 文件。
- 生成缓存、aborted runs、个人报告、本地 demo outputs 和大型本地 presentation paper copies 都会被忽略。
- 本仓库不保存任何 API key。请通过环境变量提供凭据。
