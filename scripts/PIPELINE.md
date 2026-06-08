# 🐱 Action Memory Pipeline — agent 操作手册

## 核心原则

```
每次动作前 → 检索 memory（查历史记录）
每次动作后 → 写入 memory（记下做了什么）
Case 完成   → 自动生成召回审计
```

---

## Pipeline 6 步流程（每 case）

### Step 1: fetch-papers — 阅读提供的 3 篇

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers
```

**脚本自动做的事：**
| 动作 | 说明 |
|------|------|
| 🔍 检索 memory | `pre_action_hook.sh --query "课题"`（warm 模式） |
| 📄 显示 prompt 和论文路径 | 告诉你论文在哪 |

**你需要做的事：**
1. 读 `case_detail/prompts/case_001.md`
2. 打开 `case_detail/papers/case_001/` 下的 3 篇 PDF
3. 每篇读完，在对话中执行一条：
   ```bash
   python3 scripts/append.py \
     --case-id case_001 --step 1 \
     --action-type fetch_paper \
     --target "[A] 论文标题" \
     --success true \
     --outcome "阅读完成，核心发现：..." \
     --summary-en "Core finding: ..." \
     --keywords "keyword1, keyword2" \
     --retrieve-before
   ```
   `--retrieve-before` → 写入前先检索 memory

---

### Step 2: find-DEF — 自行检索 3 篇补充论文

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step find-DEF
```

**你需要做的事：**
1. 上网搜索与课题相关的论文（优先 arXiv）
2. 每找到一篇，对话中执行：
   ```bash
   python3 scripts/append.py \
     --case-id case_001 --step 2 \
     --action-type search_paper \
     --target "[D] arXiv:xxxx" \
     --success true \
     --outcome "搜索到论文，课题相关度说明" \
     --summary-en "arxiv paper about ..." \
     --keywords "search, arxiv, 课题关键词" \
     --retrieve-before
   ```

---

### Step 3: fetch-DEF — 获取 D/E/F 全文

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step fetch-DEF
```

**你需要做的事：**
1. 用 `web_fetch` 获取论文全文
2. 每篇读完，执行：
   ```bash
   python3 scripts/append.py \
     --case-id case_001 --step 3 \
     --action-type fetch_paper \
     --target "[D] 论文标题" \
     --success true \
     --outcome "核心数据和方法..." \
     --summary-en "Key finding: ..." \
     --keywords "keyword1, keyword2" \
     --retrieve-before
   ```

---

### Step 4: read-papers — 标记阅读完成

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step read-papers
```

脚本自动写入一条 `read_papers` 记录。你也可以在读完所有论文后手动执行。

---

### Step 5: write-note — 生成研究笔记

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step write-note
```

**你需要做的事：**
1. 基于 6 篇论文撰写结构化研究笔记
2. 每写一条结论（claim），先检索再写入：
   ```bash
   python3 scripts/append.py \
     --case-id case_001 --step 8 \
     --action-type make_claim \
     --target "[A] SICA - 17%→53%" \
     --success true \
     --outcome "Tool-augmented agent 在 SWE-bench Verified 上从 17% 提升到 53%，显著优于 pure prompting" \
     --summary-en "SICA tool-augmented agent improves SWE-bench from 17% to 53%" \
     --keywords "SICA, SWE-bench, tool-augmented, agent" \
     --retrieve-before \
     --retrieve-method summary_bm25 \
     --retrieve-top-k 5 \
     --retrieve-filter "action_type=make_claim"
   ```
   注意 `--retrieve-filter "action_type=make_claim"` 限制只查同类结论，减少噪音。

3. 笔记写入 `case_detail/notes/case_001.md`

---

### Step 6: finish — 完成 + 召回审计

**入口：**
```bash
bash scripts/run_case.sh --case 001 --run 1 --step finish
```

**脚本自动做的事：**
| 动作 | 说明 |
|------|------|
| 🔍 最后一次检索 | 写 case_complete 前检索 |
| 📝 写入 complete 记录 | `append.py --case-complete` |
| 📊 生成 recall audit | 自动触发 `generate_recall_report.py` |
| 📁 输出到 memory_record | 审计报告 → `memory_record/run_1/case_001_1/` |

---

## 检索时机总览

| 动作 | 检索时机 |
|------|---------|
| `fetch_paper` 阅读前 | ✅ `pre_action_hook`（由 run_case.sh 触发）+ `--retrieve-before` |
| `search_paper` 搜索前 | ✅ `--retrieve-before` |
| `make_claim` 写结论前 | ✅ `--retrieve-before`（强制，每一步都查） |
| case_complete 完成前 | ✅ `pre_action_hook`（由 run_case.sh 触发） |

冷启动（Run 1 的 case_001~003）跳过所有检索。

---

## 4 Runs × 5 Cases 实验计划

```
Run 1: case_001~003 cold, case_004~005 warm  (记忆开始积累)
Run 2: 全部 warm                              (记忆增多)
Run 3: 全部 warm                              (记忆更多)
Run 4: 全部 warm                              (最大记忆积累)
```

查看完整计划：
```bash
bash scripts/experiment.sh
```

---

## 跨对话触发

在任何 OpenClaw 对话中：

```bash
cd ~/.openclaw/No_plan && bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers --cold
```

替换 `--case`、`--run`、`--step`、`--cold` 为你需要的值。

---

## 附录：检查你的 pipeline 是否通畅

### 检索链路检查
```bash
# 查看检索日志
python3 -c "
import json
with open('scripts/retrieve_log.jsonl') as f:
    logs = [json.loads(l) for l in f]
print(f'总检索次数: {len(logs)}')
for l in logs[-5:]:
    print(f'  {l[\"timestamp\"]} | query={l[\"query\"][:40]} | hits={l[\"hit_count\"]}')
"
```

### 记忆记录检查
```bash
python3 -c "
import json
with open('scripts/action_memory.jsonl') as f:
    records = [json.loads(l) for l in f]
print(f'总记录数: {len(records)}')
# 按 case 分组
from collections import Counter
c = Counter(r['case_id'] for r in records)
for case, n in sorted(c.items()):
    print(f'  {case}: {n} 条')
"
```

### recall audit 检查
```bash
# 查看最近生成的 recall audit
ls -la memory_record/run_1/case_001_1/
```
