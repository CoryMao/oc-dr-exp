# Action Memory 架构：完整说明与配置指南

> 版本 v3 · 2026-06-04

---

## 目录

1. [这是什么？为什么要做？](#1-这是什么为什么要做)
2. [架构总览](#2-架构总览)
3. [核心文件详解](#3-核心文件详解)
4. [怎么配置](#4-怎么配置)
5. [怎么使用（完整工作流）](#5-怎么使用完整工作流)
6. [Case 完成后生成 Recall Audit](#6-case-完成后生成-recall-audit)
7. [常见问题](#7-常见问题)

---

## 1. 这是什么？为什么要做？

### 问题

当你让 AI Agent 做多步研究任务时（比如"写一篇关于 6 篇论文的研究笔记"），Agent 会做很多动作：查论文、读论文、提取结论、写笔记。但 Agent **没有记忆**——它昨天犯过的错，今天还会再犯。

### 解决方案

Action Memory 就是给 Agent 装一个**工作日志和行为记忆系统**。每做一个动作就记录下来，下次做类似动作之前先翻翻日志，看看有没有前车之鉴。

### 三个核心步骤

```
1. 行动前  → 查历史记忆（pre_action_hook.sh）
2. 行动中  → 执行实际任务
3. 行动后  → 写下这条记录（append.py）
```

**关键是实时**：每个动作都立即记录，不是事后补录。

### 解决了你的哪些痛点

- Agent 反复踩同一个坑（如 arXiv HTML 404）→ 查 memory 得到前车之鉴
- 结论与之前的矛盾 → 查 memory 看到之前的 claim 内容
- 跨 case 知识迁移 → 检索到不同 case 下的相似经验
- 检索质量可审计 → 每个 case 结束后自动输出 recall audit 报告

---

## 2. 架构总览

### 文件清单

```
你的工作区（No_plan 目录）下：

action_memory/
├── action_memory.jsonl            ← 记忆存储文件（数据）
├── retrieve_log.jsonl             ← 检索日志（自动记录每次检索）
├── SCHEMA.md                      ← 字段说明书（文档）
├── append.py                      ← 写入工具（代码）v2 双语
├── retrieve.py                    ← 检索工具（代码）v2 三模式
├── pre_action_hook.sh             ← 行动前检索脚本（代码）v2
├── generate_recall_report.py      ← 检索审计报告生成器（代码）
├── action_memory_config.json      ← 全局配置文件（你改这个）

skills/
└── action-memory-loop/
    └── SKILL.md                   ← Agent 操作手册（文档）

memory/
└── 2026-06-04.md                  ← 长久记忆（记录工作历史和决策）
```

### 这些文件怎么配合

```
你做的事                   工具做的事
─────────                  ────────────
你改 config.json          → append.py 读到 → 写入 action_memory.jsonl
                          → retrieve.py 读到 → 检索相关经验
                          → pre_action_hook.sh 组合以上两步

Agent 做 fetch_paper 前    → pre_action_hook.sh 调用 retrieve.py
                          → 结果注入推理上下文
Agent 做完一个动作后       → append.py 写入 action_memory.jsonl
Agent 完成整个 case 后     → append.py --case-complete → 自动生成 recall audit
```

---

## 3. 核心文件详解

### 3.1 数据文件：`action_memory.jsonl`

**一句话**：所有经验的存放位置。每行一条 JSON 记录。

**示例**：

```json
{
  "case_id": "case_004",
  "step": 3,
  "action_type": "fetch_paper",
  "target": "[B] arXiv:2511.03768 Bordes What's in Common",
  "success": true,
  "outcome": "获取 HTML 全文。Common-O 基准：感知 leaderboard 饱和(80-90%)但最优模型(GPT-4o)跨场景推理仅 35%，复杂场景 <1%。53%情况幻觉出至少一个对象",
  "summary_en": "Common-O benchmark perception leaderboard saturated 80-90% GPT-4o cross scene reasoning only 35% complex scene less than 1 percent 53 percent hallucination at least one object",
  "keywords": ["Common-O", "cross scene reasoning", "hallucination", "GPT-4o", "scene graph", "leaderboard saturation"],
  "is_claim_generation": false,
  "error_type": null,
  "error_reason": null
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 什么意思 |
|------|------|------|----------|
| `case_id` | string | ✅ | 实验编号，如 `case_001`、`case_002` |
| `timestamp` | string | ✅ | 写入时间，自动生成 |
| `step` | int | ✅ | 当前实验的第几步 |
| `action_type` | string | ✅ | 动作类型（见枚举表） |
| `target` | string | 否 | 操作对象，如论文 ID |
| `success` | bool | ✅ | 是否成功 |
| `outcome` | string | 否 | 结果描述（中英均可） |
| `summary_en` | string | 否 | **英文摘要**（v2 新增，用于 BM25 英文匹配） |
| `keywords` | array | 否 | **英文关键词列表**（v2 新增，用于提升检索精度） |
| `is_claim_generation` | bool | ✅ | 是否涉及写结论/引用 |
| `error_type` | string | 否 | 失败时的错误分类 |
| `error_reason` | string | 否 | 失败具体原因 |

**action_type 枚举**：

| 值 | 什么时候用 |
|----|-----------|
| `fetch_paper` | 获取论文全文/abstract |
| `search_papers` | 检索文献 |
| `extract_claim` | 从论文中提取可引用论断 |
| `make_claim` | 撰写带引用的结论 |
| `cross_check` | 验证引用与原文是否一致 |
| `verify_citation` | 验证单条引用是否正确 |
| `other` | 其他 |

**error_type 枚举**（失败时必填）：

| 值 | 说明 |
|----|------|
| `hallucination` | 声称论文有某结论，实际没有 |
| `misattribution` | 数据来源标错标签 |
| `missing_citation` | 写了结论没标出处 |
| `out_of_context` | 曲解原文语境 |
| `fetch_fallback` | 主方案失败，走备选路线 |
| `parse_error` | 解析失败 |
| `wrong_target` | 目标对象错误 |
| `other` | 其他 |

---

### 3.2 检索日志：`retrieve_log.jsonl`

每次通过 `retrieve.py --log-retrieve` 执行的检索都会记录在此。

```json
{
  "timestamp": "2026-06-04T21:17:56+08:00",
  "query": "MLLM visual understanding",
  "method": "bm25",
  "top_k": 3,
  "action_type_filter": null,
  "only_success": false,
  "only_failure": false,
  "num_results": 3,
  "results": [
    { "score": 2.36, "case_id": "case_004", "step": 8, "action_type": "fetch_paper", ... }
  ],
  "config": { ... }
}
```

这个文件是 `generate_recall_report.py` 的数据源，用于生成每个 case 的检索审计。

---

### 3.3 写入工具：`append.py`（v2 双语）

**功能**：写入一条记录到 `action_memory.jsonl`。

**主要特性**：
- 自动填充 `timestamp`
- **自动提取英文摘要**：从中文 outcome 中提取英文 token 生成 `summary_en`
- **自动提取关键词**：从 outcome 提取高频英文词填入 `keywords`
- **支持显式传入**：也可以用 `--summary-en` 和 `--keywords` 手动指定更精确的内容
- **`--case-complete` 触发 recall audit**：写入最后一条记录后自动生成审计报告

**用法**（Agent 自动调用，你一般不需要手动执行）：

```bash
# 写入一条 fetch_paper 记录（summary_en 自动提取）
python3 action_memory/append.py \
  --case-id case_005 --step 1 \
  --action-type fetch_paper \
  --target "[A] arXiv:2505.20426" \
  --success true \
  --outcome "获取 HTML 全文。评估43个MLLM在透视理解三维度的表现" \
  --is-claim-generation false

# 显式传入更精确的英文摘要
python3 action_memory/append.py \
  --case-id case_005 --step 2 \
  --action-type make_claim \
  --target "结论1: xxx" \
  --success true \
  --outcome "中文描述" \
  --summary-en "English keywords for BM25 matching" \
  --keywords "key1, key2, key3" \
  --is-claim-generation true

# case 完成时，自动生成 recall audit
python3 action_memory/append.py \
  --case-id case_005 --step 5 \
  --action-type make_claim \
  --target "结论汇总" \
  --success true \
  --outcome "..." \
  --is-claim-generation true \
  --case-complete   # ← 自动触发 generate_recall_report.py
```

**`summary_en` 自动提取的逻辑**：
1. 从 outcome 中提取所有 >=3 字符的英文 token
2. 过滤常见停用词（`the`, `and`, `for` 等）
3. 去重、保留顺序
4. 最多 20 个 token

如果你认为自动提取不够精确，**显式传入 `--summary-en`** 是最佳实践。

---

### 3.4 检索工具：`retrieve.py`（v2 三模式）

**功能**：根据查询，从 `action_memory.jsonl` 中找出最相关的历史记录。

**三种检索模式**：

| 方法 | 描述 | 最佳使用场景 |
|------|------|-------------|
| `bm25`（默认） | 全文检索 — 对 outcome + target + summary_en + keywords 一起检索 | 中英混合 query，稳妥方案 |
| `summary_bm25` | 纯英文字段检索 — 只查 summary_en + keywords + target | **纯英文 query**，得分最高 |
| `hybrid` | 全文 BM25 + 英文 BM25 加权合并（权重 0.6:0.4） | 均衡方案，覆盖更广 |
| `tfidf` | 传统 TF-IDF 全文检索 | 备选，对比实验 |

**为什么加纯英文字段检索**：
- 用户写 query 时通常用英文（"MLLM hallucination cross scene reasoning"）
- 但 outcome 是中文，BM25 对中文做 char-level + bigram tokenization，英文 query 的 token 在中文文段中匹配率极低
- `summary_en` + `keywords` 是纯英文，query 中的英文关键词直接命中，得分大幅提升

**用法**：

```bash
# BM25 全文检索（默认）
python3 action_memory/retrieve.py --query "MLLM perspective benchmark"

# 纯英文字段检索（推荐英文 query）
python3 action_memory/retrieve.py --query "cross scene reasoning hallucination" --method summary_bm25

# 混合模式
python3 action_memory/retrieve.py --query "abstract visual reasoning rule binding" --method hybrid

# 按 action_type 过滤
python3 action_memory/retrieve.py --query "perspective benchmark" --action-type fetch_paper

# 只看失败经验
python3 action_memory/retrieve.py --query "fetch fail 404" --only-failure

# 显示详细内容 + 记录检索日志
python3 action_memory/retrieve.py --query "rule binding" --show-report --log-retrieve

# JSON 输出（程序消费用）
python3 action_memory/retrieve.py --query "data leakage" --json-output
```

**BM25 的核心原理**（通俗版）：
- 查询中出现的词在文档中出现越多次 → 越相关
- 但太常见的词（"的"、"获取"）权重低
- 罕见的词（"R-F chasm"、"51.2%"）一旦出现就权重很高
- 文档长度越长权重越低（惩罚长文档）

---

### 3.5 行动前检索脚本：`pre_action_hook.sh`（v2）

**功能**：在每次关键动作之前，自动执行检索并输出结果。

这是 Agent 在执行时的**入口**。它替代了手动调用 `retrieve.py`。

```bash
./action_memory/pre_action_hook.sh \
  --action-type fetch_paper \
  --query "MLLM perspective benchmark" \
  --target "[A] MMPerspective" \
  [--method summary_bm25] \
  [--top-k 5]
```

**这个脚本自动完成以下事情**：

1. **检查配置**：`enable` 是否为 `true`
2. **检查 action_type 是否在 `require_retrieve_before` 列表中**
3. **调用 `retrieve.py`**：使用 `--log-retrieve --show-report`
4. **输出检索结果**：分条展示命中的记录、score、outcome 摘要
5. **记录检索日志**：追加到 `retrieve_log.jsonl`

**推荐的方法搭配**：

| query 语言 | 推荐 method |
|-----------|-------------|
| 纯英文 | `--method summary_bm25`（得分最高） |
| 中英混合 | 默认 `bm25` 即可 |
| 想兼顾两者 | `--method hybrid` |

**`require_retrieve_before` 列表中包含的 action_type**（在 `action_memory_config.json` 配置）：

```
fetch_paper, search_papers, make_claim, cross_check, verify_citation
```

不在列表中的 action_type（如 `other`、`extract_claim`）会**跳过检索**。

---

### 3.6 检索审计报告生成器：`generate_recall_report.py`

**功能**：基于 `retrieve_log.jsonl`，按 case_id 输出每步检索的详细审计报告。

**用法**：

```bash
# 查看某个 case 的详细检索日志
python3 action_memory/generate_recall_report.py --case-id case_004

# 输出到 Markdown 文件
python3 action_memory/generate_recall_report.py --case-id case_004 --output recall_audit_case4.md

# 查看所有 case 的汇总
python3 action_memory/generate_recall_report.py

# 只看 0 命中的检索（冷启动 / 首次探索）
python3 action_memory/generate_recall_report.py --show-zeros

# 只看最近几次
python3 action_memory/generate_recall_report.py --recent 5

# 输出到文件（同时打印概要）
python3 action_memory/generate_recall_report.py --case-id case_004 --output recall_audit_case4.md
```

**报告包含**：

- **Overview 统计**：总检索次数、命中数、零命中率、same-case/cross-case 比例
- **每条检索详情**：时间、query、method、top_k、命中条目（含 score / hit relation / outcome 节略）
- **Hit Relation 标记**：`same-case`（同一 case 的记录）、`cross-case(xxx)`（跨 case 的记录）

**自动触发**：在 `append.py` 加上 `--case-complete` 后，会自动调用此脚本生成对应 case 的 audit。

**典型落地方式**（Case 结束时）：

```bash
python3 action_memory/append.py \
  --case-id case_005 --step 12 \
  --action-type make_claim \
  --target "研究结论汇总" \
  --success true \
  --outcome "完成了6篇论文的逐条分析，输出8条结论" \
  --is-claim-generation true \
  --case-complete
# → 自动生成 recall_audit_case_005.md
```

---

### 3.7 Agent 操作手册：`SKILL.md`

> 路径：`skills/action-memory-loop/SKILL.md`

这是 Agent 的行为准则说明书，包含：
- **启动条件**：做文献研究/实验/多步推理任务时自动激活
- **核心规则**：行动前检索 → 行动后立即写入 → 禁止事后补录
- **方法选择指南**：纯英文 query 用 `summary_bm25`，中英混合用 `bm25`
- **枚举表**：action_type、error_type
- **Case 完成时**：生成 recall audit 的流程

**你不需要编辑这个文件**，除非想改变 Agent 的行为规则。配置参数改 `action_memory_config.json`。

---

## 4. 怎么配置

**你只需要编辑 `action_memory_config.json`**。

### 完整内容

```json
{
  "version": "v2",
  "memory_file": "action_memory.jsonl",
  "enable": true,
  "default_top_k": 3,
  "cold_start": {
    "skip_retrieve_for_first_n_cases": 3,
    "skip_retrieve_for_first_n_steps": 0
  },
  "retrieve_monitor": {
    "log_enabled": true,
    "log_file": "retrieve_log.jsonl",
    "show_report_by_default": true
  },
  "require_retrieve_before": [
    "fetch_paper",
    "search_papers",
    "make_claim",
    "cross_check",
    "verify_citation"
  ],
  "require_append_after": [
    "fetch_paper",
    "search_papers",
    "make_claim",
    "extract_claim",
    "cross_check",
    "verify_citation"
  ],
  "injection": {
    "max_experiences_to_inject": 2,
    "inject_success_too": true,
    "inject_failures_too": true
  },
  "recommended_method": "bm25",
  "retrieve_methods": {
    "bm25": "全文中英混合",
    "summary_bm25": "仅英文字段，英文query推荐",
    "hybrid": "全文+英文摘要加权合并"
  }
}
```

### 各参数详解

#### `enable`
- `true`：开启整个机制
- `false`：关闭，Agent 不查也不写

#### `default_top_k`
每次检索返回的条数。3 是合适的默认值，data 多时可以调大到 5。

#### `cold_start`

两个子参数：

| 参数 | 含义 |
|------|------|
| `skip_retrieve_for_first_n_cases` | 前 N 个 case 跳过检索（记忆为空时检索无意义） |
| `skip_retrieve_for_first_n_steps` | 每个 case 的前 N 步跳过检索 |

典型配置：
- 刚开始用 → `skip_retrieve_for_first_n_cases: 2`（前 2 个 case 不检索）
- 已有足够记录 → `skip_retrieve_for_first_n_cases: 0`（每次都检索）

#### `require_retrieve_before`
哪些 action_type 在执行前要检索：

```json
["fetch_paper", "search_papers", "make_claim", "cross_check", "verify_citation"]
```

如果不希望某个类型检索，从列表移除即可。

#### `require_append_after`
哪些 action_type 在执行后要写入记录。一般所有重要操作都应该记录。

#### `injection`
检索到经验后，把多少条注入推理上下文：

| 参数 | 含义 |
|------|------|
| `max_experiences_to_inject` | 最多注入 2 条经验 |
| `inject_success_too` | 是否注入成功经验 |
| `inject_failures_too` | 是否注入失败经验 |

两个都设 `true` = 成败都看。

#### `recommended_method`
推荐默认的检索方法：`"bm25"`（全文覆盖广），纯英文 query 场景可以手动指定 `summary_bm25`。

#### `retrieve_methods`
各方法的简要说明（文档用途，不影响代码逻辑）。

### 不同场景的配置建议

| 场景 | cold_start | default_top_k | injection |
|------|-----------|---------------|-----------|
| 刚开始（0 条记录） | cases=2, steps=3 | 2 | 1 |
| 中等规模（20+ 条） | cases=0, steps=0 | 3 | 2 |
| 大规模（100+ 条） | cases=0, steps=0 | 5 | 3 |

---

## 5. 怎么使用（完整工作流）

这套系统是 **Agent 自动运行的**。为了让用户理解整个过程，这里展开说明。

### 开始一个新 Case

你告诉 Agent："帮我研究 MLLM 是否具备类人视觉理解能力，论文有 [A][B][C]"

### Agent 内部执行的工作流

#### Step 1: Fetch [A] 之前

Agent 执行：

```bash
./action_memory/pre_action_hook.sh \
  --action-type fetch_paper \
  --query "MLLM perspective benchmark" \
  --target "[A] arXiv:2505.20426 MMPerspective"
```

**检索结果** ↓

```
[1] score=4.18  [case_003:step7] fetch_paper (binding affinity 的 benchmark 讨论)
[2] score=2.98  [case_003:step9] make_claim
[3] score=2.36  [case_004:step8] fetch_paper (Hyperphantasia)
```

→ 虽然跨 case 有噪声，但 top-3 显示了之前 fetch 论文的经验

→ Agent 将这些注入推理上下文

#### Step 2: 实际 fetch [A]

```bash
web_fetch https://arxiv.org/html/2505.20426
```

#### Step 3: 写入记录

```bash
python3 action_memory/append.py \
  --case-id case_004 --step 1 \
  --action-type fetch_paper \
  --target "[A] arXiv:2505.20426" \
  --success true \
  --outcome "获取 HTML 全文。评估43个MLLM在透视理解三维度的表现..." \
  --is-claim-generation false
```

#### Step 4-N: 重复以上三步

每做 fetch / search / claim 之前都先查 memory，做完立即写入。

#### 最后一步：Case 完成

```bash
python3 action_memory/append.py \
  --case-id case_004 --step 9 \
  --action-type make_claim \
  --target "研究结论汇总" \
  --success true \
  --outcome "完成7条逐条结论..." \
  --is-claim-generation true \
  --case-complete
```

→ 自动触发 `generate_recall_report.py --case-id case_004 --output recall_audit_case4.md`

### 关于 `summary_en` 的写作建议

> 观察发现：**写入时越用心写 summary_en，检索时效果越好**

推荐做法：

| action 类型 | summary_en 示例 |
|-------------|----------------|
| fetch_paper 成功 | `"MMPerspective benchmark 43 MLLMs perspective perception reasoning robustness GPT-4o Gemini-2-flash 57.7% far from saturation"` |
| fetch_paper 失败 | `"FAILED bioRxiv Cloudflare 403 Nature MI paywall cannot fetch full text"` |
| make_claim | `"case 4 summary MLLM visual understanding six papers not human-like surface tasks okay structural reasoning breaks down"` |

关键原则：
1. **包含具体数字**：57.7%、78.8%、51.2%
2. **包含论文方法名**：MMPerspective、Common-O、VisFactor
3. **包含核心结论**：far from saturation、cross scene reasoning only 35%
4. **简短优先**：一行内说完，不需要句子结构

---

## 6. Case 完成后生成 Recall Audit

### 为什么需要 Recall Audit

在每个 case 结束后，复盘检索质量：

| 指标 | 含义 | 理想值 |
|------|------|--------|
| same-case 占比 | 命中是否来自当前 case | > 60% |
| cross-case 噪声 | 命中来自其他 case 的无效内容 | < 30% |
| 零命中率 | 检索什么都没找到 | < 10% |

### 两种触发方式

**方式一：自动触发（推荐）**

在 case 最后的 append 命令加 `--case-complete`：

```bash
python3 action_memory/append.py \
  --case-id case_005 --step 12 \
  --action-type make_claim \
  --target "结论汇总" \
  --success true \
  --outcome "..." \
  --is-claim-generation true \
  --case-complete
```

→ 自动输出 `action_memory/recall_audit_case_005.md`

**方式二：手动触发**

```bash
python3 action_memory/generate_recall_report.py \
  --case-id case_005 \
  --output recall_audit_case5.md
```

### Audit 报告的结构

```
# Action Memory Recall Audit — case_004

## Overview

- Total retrievals: 7
- Total hits: 19 (avg 2.7/retrieval)
- Zero-hit retrievals: 0 (0%)
- Same-case hits: 14 (74%)
- Cross-case hits: 5 (26%)

## Retrieval Log Detail

### #1: 2026-06-04T21:17:56+08:00
- Context: case_004
- Query: MLLM visual understanding
- Method: bm25 | top_k: 3
- Hits: 3

| Score | Hit Relation | Success | Case:Step | Action Type | Outcome Excerpt |
|-------|-------------|---------|-----------|-------------|-----------------|
| 2.36  | same-case   | ✅      | case_004:step8 | fetch_paper | 获取HTML全文... |
| 2.22  | same-case   | ✅      | case_004:step2 | fetch_paper | 获取HTML全文... |
| 2.18  | same-case   | ✅      | case_004:step4 | fetch_paper | 获取HTML全文... |
```

### 本系统实测的检索效果

从 Case 1-4 共 19 次检索的审计数据：

| 指标 | 数值 |
|------|------|
| 总检索次数 | 19 |
| 总命中数 | 49（均 2.6 条/次） |
| 零命中率 | 5%（1/19） |
| same-case 命中率 | 80%（39/49） |
| cross-case 噪声率 | 20%（10/49） |

双语优化后（summary_bm25/hybrid）对纯英文 query 的改善尤为明显——"cross scene reasoning hallucination" 从 0 条提升到 3 条最高 16.46 分。

---

## 7. 常见问题

### Q1：这个系统和 OpenClaw 自带的 memory 系统有什么区别？

OpenClaw 的 memory（`memory/` 目录下的 `.md` 文件 + `memory_search` 工具）用来存**对话上下文、用户偏好、长期知识**。Action Memory 是用来存**行为日志**的——每一步做了什么、结果如何、遇到了什么坑。

两者互补，不冲突。

### Q2：`summary_en` 自动提取不够精确怎么办？

两种改善方式：

1. **写入时显式传入**：`--summary-en "MLLM perspective GPT-4o 57.7% far from saturation"`
2. **事后修复**：直接编辑 `action_memory.jsonl`，找到对应记录修改 `summary_en` 字段

对于 Case 4 的记录，我们做了第二种方式的批量修复（共 8 条记录）。

### Q3：纯中文 outcome 的 BM25 分数为什么偏低？

BM25 使用 char-level + bigram 对中文 tokenize。如果 query 是纯英文（"cross scene reasoning hallucination"），而 outcome 是中文（"跨场景推理仅35%"），中英字符在 tokenization 时被分开处理，英文 token 在中文文段中出现的概率很低。

**解决方案**：
- 写入时填 `summary_en`（纯英文，BM25 直接匹配）
- 检索时用 `--method summary_bm25`（只查英文字段）

### Q4：`recommended_method` 选哪个？

| 你的 query 风格 | 推荐 method | 原因 |
|---------------|-------------|------|
| 纯英文（"MLLM hallucination cross scene"） | `summary_bm25` | 纯英文字段匹配，得分最高 |
| 中英混合（"MLLM 透视 benchmark 57.7%"） | `bm25`（默认） | 全文检索，中文命中 outcome，命中英文 summary_en |
| 稳妥，想要覆盖广 | `bm25` | 默认选项，覆盖中英 |
| 更均衡 | `hybrid` | 全文 BM25 + 英文 BM25 加权合并 |

### Q5：`--case-complete` 生成的 audit 文件在哪？

在 `action_memory/` 下，文件名是 `recall_audit_{case_id}.md`。

例如 `--case-id case_005` 会生成 `action_memory/recall_audit_case_005.md`。

### Q6：记录越来越多，`retrieve.py` 会变慢吗？

当前 64 条记录下检索是毫秒级的（BM25 纯 Python 实现）。预计 1000 条以下都在亚秒级。如果真的很大了（几千条以上），可以按 case_id 分区归档旧数据。

### Q7：我改了配置但没生效？

检查 JSON 格式是否正确：

```bash
python3 -m json.tool action_memory/action_memory_config.json
```

无输出 = 格式正确。有报错说明少引号或多逗号。

### Q8：`.case_manager.py` 去哪里了？

v1 设计稿中有 `case_manager.py` 的规划，但最终实现中**没有使用它**。原因是：
- Agent 可以手动维护 step 序号（从 1 递增）
- 不需要额外的状态文件
- 减少系统复杂性

如果你发现 step 管理困难（跨会话），可以恢复 `case_manager.py` 或直接在 append.py 中加 `--auto-step` 逻辑。

---

## 附录：文件路径速查

| 文件 | 路径（相对 workspace 根目录） |
|------|-----------------------------|
| 记忆数据 | `action_memory/action_memory.jsonl` |
| 检索日志 | `action_memory/retrieve_log.jsonl` |
| 配置文件 | `action_memory/action_memory_config.json` |
| 写入工具 | `action_memory/append.py` |
| 检索工具 | `action_memory/retrieve.py` |
| 行动前检索脚本 | `action_memory/pre_action_hook.sh` |
| Recall Audit 生成器 | `action_memory/generate_recall_report.py` |
| 字段说明书 | `action_memory/SCHEMA.md` |
| 本指南 | `action_memory/ACTION_MEMORY_GUIDE.md` |
| Agent 操作手册 | `skills/action-memory-loop/SKILL.md` |
| 长久记忆 | `memory/2026-06-04.md` |

---

## 快速卡片（一张图记住）

```
                    ┌─────────────────────┐
                    │  action_memory_config.json │
                    │  （你在这里改配置）        │
                    └──────────┬──────────┘
                               │
     ┌───────────────┐         │         ┌─────────────────┐
     │ pre_action_   │         │         │  append.py      │
     │ hook.sh       │◄────────┴────────►│  v2 双语写入    │
     │ 检索入口       │  检索并写入       │  +--case-complete│
     └───────┬───────┘                  └────────┬─────────┘
             │                                   │
             ▼                                   ▼
     ┌───────────────┐                  ┌─────────────────┐
     │  retrieve.py  │                  │  action_memory.  │
     │  v2 三模式     │◄───── 读 ───────►│  jsonl          │
     │  bm25/summary  │                  │  64 条记录      │
     │  _bm25/hybrid  │                  └────────┬─────────┘
     └───────┬───────┘                           │
             │                                   ▼
             │                      ┌─────────────────────┐
             │                      │ generate_recall_    │
             └─────── 读 ──────────►│ report.py           │
                       检索日志      │ 按 case 输出 audit  │
                                    └─────────────────────┘
```
