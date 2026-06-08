# 🐱 Action Memory 系统说明文档

> 版本: v3 | 最后更新: 2026-06-05
> 作者: 金咪（电子猫 🐱）

## Repository note

This directory is kept in the project repository as the toolchain for an auxiliary action-memory side experiment. It is not the formal main-memory implementation used by `runs/main_memory/M1_memory_on/`.

The JSONL files in this directory are working snapshots/examples for the toolchain, not complete formal experiment logs. In `action_memory.jsonl`, `error_type` and `error_reason` are manual audit fields filled after human review; they are not generated automatically by the agent.

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    No_plan/ 工作区                        │
│                                                          │
│  scripts/              case_detail/        memory_record/ │
│  ├─ append.py          ├─ prompts/         ├─ run_1/     │
│  ├─ retrieve.py        ├─ papers/          ├─ run_2/     │
│  ├─ pre_action_hook.sh ├─ notes/           ├─ run_3/     │
│  ├─ run_case.sh                           └─ run_4/     │
│  ├─ experiment.sh                                        │
│  ├─ generate_recall_report.py          memory/            │
│  ├─ action_memory_config.json          ├─ YYYY-MM-DD.md  │
│  ├─ action_memory.jsonl                                  │
│  ├─ retrieve_log.jsonl                 (旧文件不删除)    │
│  ├─ PIPELINE.md                        action_memory/    │
│  └─ ACTION_MEMORY_GUIDE.md             research_note_*   │
└─────────────────────────────────────────────────────────┘
```

### 数据流向

```
Agent 动作
    │
    ▼
pre_action_hook.sh ──检索──▶ retrieve.py ──写入──▶ retrieve_log.jsonl
    │
    ▼
Agent 完成任务
    │
    ▼
append.py ──写入──▶ action_memory.jsonl
    │                   │
    │      ┌────────────┘
    │      ▼
    │   (case_complete?)
    │      │ 是
    │      ▼
    │   generate_recall_report.py ──▶ memory_record/run_X/case_XXX_X/
    │
    └── (retrieve_before?) ──▶ retrieve.py（写入前再查一次）
```

---

## 二、每个文件干什么

### 2.1 核心引擎

| 文件 | 大小 | 用途 |
|------|------|------|
| `scripts/append.py` | 12K, 241 行 | **写入 action memory**。每次动作完成后调用。自动生成 `summary_en`（英文摘要）和 `keywords`（关键词）。支持 `--retrieve-before`（写入前检索）和 `--case-complete`（完成时自动触发 recall audit） |
| `scripts/retrieve.py` | 20K, 457 行 | **检索引擎**。四种检索方法：bm25（全文中英混合）、summary_bm25（仅英文字段）、hybrid（加权合并）、tfidf。支持按 action_type 过滤、按成功/失败过滤。每次检索结果自动写入 `retrieve_log.jsonl` |
| `scripts/generate_recall_report.py` | 12K, 295 行 | **召回审计报告生成**。分析某 case 的检索记录，计算命中率、same-case 占比、跨 case 知识迁移量。支持 `--case-id`、`--recent`、`--show-zeros` 过滤 |

### 2.2 触发入口

| 文件 | 大小 | 用途 |
|------|------|------|
| `scripts/run_case.sh` | 12K, 296 行 | **一键 Case 启动**。分成 6 步（fetch-papers → find-DEF → fetch-DEF → read-papers → write-note → finish）。每步自动触发检索和写入。跨对话入口：`bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers --cold` |
| `scripts/pre_action_hook.sh` | 8K, 121 行 | **动作前检索钩子**。在关键动作之前调用，查询 action memory 并打印检索结果。本质上是对 `retrieve.py` 的一层 shell 封装 |
| `scripts/experiment.sh` | 4K, 74 行 | **实验编排**。打印 4 runs × 5 cases 完整实验计划，列出每步可复制的命令 |

### 2.3 配置与文档

| 文件 | 大小 | 用途 |
|------|------|------|
| `action_memory_config.json` | 4K | **全局配置**。控制检索开关、默认 top_k、冷启动规则、require_retrieve_before 列表、require_append_after 列表 |
| `action_memory.jsonl` | 62K | **记忆数据库**。每行一条 JSON 记录，当前 80 条 |
| `retrieve_log.jsonl` | 44K | **检索日志**。每次检索的查询、方法、命中结果全量记录，当前 23 条 |
| `PIPELINE.md` | 8K, 228 行 | **操作手册**。告诉 agent 每一步该做什么 |
| `ACTION_MEMORY_GUIDE.md` | 28K, 789 行 | **详细技术文档**。schema 设计、配置选项、检索方法原理、召回审计解读 |

### 2.4 目录

| 目录 | 用途 |
|------|------|
| `case_detail/prompts/` | 5 个 case 的 prompt（README.md 格式） |
| `case_detail/papers/case_XXX/` | 每个 case 提供的 3 篇论文 PDF（共 15 篇） |
| `case_detail/notes/` | 研究笔记输出 |
| `memory_record/run_X/case_XXX_X/` | 每个 case 每次 run 的召回审计报告 |

---

## 三、Memory 当前能力

### 3.1 检索能力

| 方法 | 原理 | 适用场景 |
|------|------|----------|
| `bm25` （默认） | 中英文全文 BM25 检索 | 通用查询，中英混合 |
| `summary_bm25` | 仅搜 `summary_en` + `keywords` 字段 | 纯英文 query，结果更干净 |
| `hybrid` | 全文 BM25 + 英文摘要 BM25 加权合并 | 需要平衡中英文覆盖面 |
| `tfidf` | TF-IDF 向量化 + 余弦相似度 | 对比实验或短文本 |

### 3.2 记录能力

- **80 条记录**，分属 6 个 case（case_001 ~ case_005 + test_bilingual）
- 每条记录包含：`case_id`、`step`、`action_type`、`target`、`success`、`outcome`、`summary_en`、`keywords`、`context`、`error` 字段
- **100% 覆盖英文摘要和关键词**（summary_en: 80/80, keywords: 80/80）
- action_type 分布：`fetch_paper` (37) + `search_paper` (8) + `make_claim` (31) + `write_note` (3) + `case_complete` (1)

### 3.3 审计能力

`generate_recall_report.py` 可以回答：
- 这个 case 检索了多少次？每次命中多少？
- 命中记录中，同一个 case 的占多少？（same-case \%）
- 跨 case 的知识迁移有多少？（cross-case）
- 哪些检索 0 命中？
- 检索质量随 run 次数增加如何变化？

### 3.4 自动化能力

| 事件 | 自动行为 |
|------|---------|
| 每次 fetch_paper / make_claim 前 | `--retrieve-before` 触发检索 |
| 每次动作完成后 | `append.py` 写入 jsonl |
| `--case-complete` | 自动调用 `generate_recall_report.py` 生成审计 |
| cold_start 模式 | 前 3 个 case 首次 run 自动跳过检索 |

---

## 四、可调参数

### 4.1 action_memory_config.json

```json
{
  "enable": true,                          // 是否启用 action memory
  "default_top_k": 3,                      // 默认检索返回条数
  "cold_start": {
    "skip_retrieve_for_first_n_cases": 3,  // 前 N 个 case 跳过检索
    "skip_retrieve_for_first_n_steps": 0   // 前 N 个 step 跳过检索
  },
  "require_retrieve_before": [             // 哪些 action 必须检索
    "fetch_paper", "make_claim", ...
  ],
  "require_append_after": [               // 哪些 action 必须写入
    "fetch_paper", "make_claim", ...
  ],
  "injection": {
    "max_experiences_to_inject": 2,        // 最多注入几条经验
    "inject_success_too": true,            // 是否注入成功记录
    "inject_failures_too": true            // 是否注入失败记录
  },
  "recommended_method": "bm25"             // 推荐检索方法
}
```

### 4.2 run_case.sh 参数

| 参数 | 说明 |
|------|------|
| `--case 001` | case 编号 |
| `--run 1` | run 编号 (1-4) |
| `--step fetch-papers / find-DEF / fetch-DEF / read-papers / write-note / finish` | 执行步骤 |
| `--cold` | 冷启动，跳过检索 |
| `--dry-run` | 只打印计划不执行 |

### 4.3 retrieve.py 参数

| 参数 | 说明 |
|------|------|
| `--query "..."` | 检索查询（必填） |
| `--method bm25 / summary_bm25 / hybrid / tfidf` | 检索方法 |
| `--top-k 5` | 返回条数 |
| `--action-type make_claim` | 按 action_type 过滤 |
| `--only-success / --only-failure` | 只查看成功/失败的记录 |
| `--show-report / -r` | 打印检索报告 |
| `--log-retrieve` | 记录到 retrieve_log.jsonl |
| `--json-output` | 输出 JSON 格式 |

### 4.4 append.py 参数

| 参数 | 说明 |
|------|------|
| `--case-id, --step, --action-type` | 必填。标识一条记录 |
| `--success true/false` | 必填。是否成功 |
| `--outcome "..."` | 详细的中文结果描述 |
| `--summary-en "..."` | 英文摘要（不传则自动从 outcome 提取英文 token） |
| `--keywords "a, b, c"` | 逗号分隔的关键词（不传则自动提取） |
| `--retrieve-before` | 写入前自动检索 memory |
| `--retrieve-query "..."` | 检索查询词（不传则用 summary_en 或 outcome） |
| `--retrieve-method summary_bm25` | 检索方法 |
| `--retrieve-top-k 5` | 检索条数 |
| `--retrieve-filter "action_type=make_claim"` | 检索过滤 |
| `--case-complete` | 标记 case 完成，自动触发 recall audit |
| `--json file.json` | 从 JSON 文件读取记录，适用于复杂场景 |

### 4.5 pre_action_hook.sh 参数

| 参数 | 说明 |
|------|------|
| `--action-type` | 当前动作类型，用于检索优化（必填） |
| `--query` | 检索查询（必填） |
| `--target` | 当前目标 |
| `--method` | 检索方法，默认从 config 读取 |
| `--top-k` | 检索条数，默认从 config 读取 |

---

## 五、如何给其他 workspace 的 agent 使用

### 方案 A：新 workspace 的 agent 直接调用本 scripts/

在新 workspace 中，用 `exec` 或 `web_fetch` 指向本 workspace：

```bash
# 直接调用（路径不变）
bash /home/mayli/.openclaw/No_plan/scripts/run_case.sh --case 001 --run 1 --step fetch-papers

# 或从文件中读取文档
cat /home/mayli/.openclaw/No_plan/scripts/PIPELINE.md
```

### 方案 B：让新 agent 理解 memory 系统

给新 agent 的 prompt 开头加上：

```
你有权访问 action memory 系统，位于 /home/mayli/.openclaw/No_plan/scripts/

使用方法：
1. 每次 fetch 论文前：python3 scripts/append.py --retrieve-before ...（写入前自动检索）
2. 每次写 claim 前：python3 scripts/append.py --retrieve-before --retrieve-filter "action_type=make_claim" ...
3. 每次动作后：python3 scripts/append.py --case-id ... --action-type ... （写入记录）
4. case 完成：python3 scripts/append.py --case-complete ...（自动生成召回审计）

详细说明见：PIPELINE.md
```

### 方案 C：软链接（让路径变短）

```bash
ln -s /home/mayli/.openclaw/No_plan/scripts /home/mayli/.openclaw/你的workspace/am
```

这样在你的 workspace 中执行：

```bash
bash am/run_case.sh --case 001 --run 1 --step fetch-papers
```

### 方案 D：复制到新 workspace

```bash
cp -r /home/mayli/.openclaw/No_plan/scripts /home/mayli/.openclaw/你的新workspace/am
cp /home/mayli/.openclaw/No_plan/case_detail /home/mayli/.openclaw/你的新workspace/
```

注意：复制后要更新 `scripts/action_memory_config.json` 中的 `memory_file` 路径。

---

## 六、快速参考

### 常用命令速查

```bash
# 1. 开始一个 case
bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers --cold

# 2. 阅读论文后记录
python3 scripts/append.py \
  --case-id case_001 --step 1 \
  --action-type fetch_paper --target "[A] SICA" --success true \
  --outcome "核心发现：tool-augmented agent 17%→53% in SWE-bench" \
  --summary-en "SICA improves SWE-bench from 17% to 53%" \
  --keywords "SICA, SWE-bench, tool-augmented, agent"

# 3. 写 claim（写入前检索）
python3 scripts/append.py \
  --case-id case_001 --step 8 \
  --action-type make_claim --target "[A] SICA" --success true \
  --outcome "Tool-augmented agent 显著优于 pure prompting" \
  --retrieve-before

# 4. 完成 case
bash scripts/run_case.sh --case 001 --run 1 --step finish

# 5. 查看 recall audit
cat memory_record/run_1/case_001_1/recall_audit_case_001.md

# 6. 查看实验计划
bash scripts/experiment.sh
```

### 参数调优建议

| 场景 | 推荐 method | 推荐 top_k |
|------|-------------|------------|
| 默认 | `bm25` | 3-5 |
| 英文 query 想干净 | `summary_bm25` | 3-5 |
| 需要覆盖中英文 | `hybrid` | 5-8 |
| 短文本对比实验 | `tfidf` | 5 |
| 写 claim 前检索 | `summary_bm25` + filter | 5 |
