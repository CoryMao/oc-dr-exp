#!/usr/bin/env bash
# =============================================================================
# OpenClaw 科研 Agent 现场展示 — 运行脚本
# =============================================================================
# 用法:
#   bash demo/run.sh --pdf paper.pdf --topic "研究课题"
#   bash demo/run.sh --pdf paper.pdf --topic "研究课题" --timeout 1200
#
# 输出: demo/outputs/<timestamp>/ 下的 ORIGINAL_REPORT, REFCHECKER_REPAIR_LOG,
#       REPAIRED_REPORT, RUN_SUMMARY
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROFILE="openclaw-demo"
WORKSPACE="$HOME/.openclaw-${PROFILE}/workspace"
TIMESTAMP="$(date -u '+%Y%m%dT%H%M%SZ')"
OUTPUT_DIR="$SCRIPT_DIR/outputs/$TIMESTAMP"

# ── 参数解析 ──────────────────────────────────────────────────────
PDF_PATH=""
TOPIC=""
TIMEOUT=1800
THINKING="high"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pdf)   PDF_PATH="$2";   shift 2 ;;
    --topic) TOPIC="$2";      shift 2 ;;
    --timeout) TIMEOUT="$2";  shift 2 ;;
    --thinking) THINKING="$2"; shift 2 ;;
    *)
      echo "未知参数: $1"
      echo "用法: bash demo/run.sh --pdf <PDF路径> --topic <研究课题> [--timeout <秒>] [--thinking <level>]"
      exit 1
      ;;
  esac
done

if [[ -z "$PDF_PATH" || -z "$TOPIC" ]]; then
  echo "用法: bash demo/run.sh --pdf <PDF路径> --topic <研究课题>"
  echo ""
  echo "参数:"
  echo "  --pdf       PDF 文件路径（必填）"
  echo "  --topic     研究课题（必填）"
  echo "  --timeout   超时秒数（默认 1800）"
  echo "  --thinking  thinking level（默认 high）"
  exit 1
fi

if [[ ! -f "$PDF_PATH" ]]; then
  echo "❌ PDF 文件不存在: $PDF_PATH"
  exit 1
fi

PDF_REALPATH="$(cd "$(dirname "$PDF_PATH")" && pwd)/$(basename "$PDF_PATH")"
PDF_NAME="$(basename "$PDF_REALPATH")"
SESSION_KEY="demo-${TIMESTAMP}"

echo "============================================"
echo " OpenClaw Demo Run"
echo "============================================"
echo "  PDF:    $PDF_REALPATH"
echo "  课题:   $TOPIC"
echo "  超时:   ${TIMEOUT}s"
echo "  输出:   $OUTPUT_DIR"
echo "============================================"
echo ""

# ── 0. 网络环境：课堂 demo 默认复用本机代理 ───────────────────────
if [[ "${OPENCLAW_DEMO_AUTO_PROXY:-1}" != "0" ]]; then
  if [[ -z "${HTTPS_PROXY:-}" && -z "${https_proxy:-}" ]] && command -v nc >/dev/null 2>&1 && nc -z 127.0.0.1 7897 >/dev/null 2>&1; then
    export HTTPS_PROXY="http://127.0.0.1:7897"
    export HTTP_PROXY="http://127.0.0.1:7897"
    echo "✅ 已自动启用本机代理: http://127.0.0.1:7897"
  fi
fi

DEMO_NO_PROXY="api.deepseek.com,arxiv.org,export.arxiv.org,localhost,127.0.0.1"
if [[ -n "${NO_PROXY:-}" ]]; then
  export NO_PROXY="$DEMO_NO_PROXY,$NO_PROXY"
else
  export NO_PROXY="$DEMO_NO_PROXY"
fi
export no_proxy="$NO_PROXY"

# ── 1. 确保 profile 存在 ─────────────────────────────────────────
if ! openclaw --profile "$PROFILE" config validate 2>/dev/null; then
  echo "❌ Profile '${PROFILE}' 未配置，请先运行: bash demo/setup.sh"
  exit 1
fi

# ── 2. 复制 PDF 到 workspace ─────────────────────────────────────
mkdir -p "$WORKSPACE/input_papers"
cp "$PDF_REALPATH" "$WORKSPACE/input_papers/$PDF_NAME"
echo "✅ PDF 已复制到 workspace: input_papers/$PDF_NAME"

# ── 3. 生成 prompt ────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"

PROMPT_FILE="$OUTPUT_DIR/prompt.md"

cat > "$PROMPT_FILE" << 'PROMPTEOF'
你是一名科研助理。你需要基于给定课题和论文材料撰写一份结构化研究笔记。

本任务分为三个阶段，必须在同一次最终回复中按顺序输出。

---

## 阶段 1：生成未修复初稿 ORIGINAL_REPORT

### 硬性规则

- 阶段 1 不得调用 refchecker / verify_citation。
- 你必须阅读 workspace 中 input_papers/ 下的 PDF 论文。
- 你必须自行检索并获取至少三篇高度相关的开放获取论文，标记为 [D]、[E]、[F]。
- 最终报告只能引用 [A]~[F] 六篇论文（[A] 为提供的 PDF）。
- 第二部分每条结论必须有 [A]~[F] 出处标签和 CPS 位置标注。

### 课题

PROMPTEOF

echo "$TOPIC" >> "$PROMPT_FILE"

cat >> "$PROMPT_FILE" << 'PROMPTEOF'

### 提供的论文 PDF

PDF 文件位于 workspace 的 input_papers/ 目录下。标记为 [A]。

你需要自行获取论文元信息（标题、作者、年份、arXiv ID 或 DOI）。

### 自主检索要求

- 使用 arxiv MCP 或 web_search 检索 [B]~[F] 五篇高度相关论文。
- 优先选择 2024–2025 年开放获取论文。
- 优先选择与课题直接相关的论文。

### ORIGINAL_REPORT 格式

必须包含以下三个部分，总计约 600–800 中文字：

#### 第一部分：总体评估

基于全部六篇论文，概括当前证据状况、共识/分歧、局限或 gap。

#### 第二部分：逐条结论

提取 5–8 条具体、可被证伪的结论。每条使用：

```text
- 结论陈述。
  出处：[A] §N.M::¶K / [B] §N.M::TK
```

所有引用位置必须遵守 CPS 格式（citation-standard skill）。

#### 第三部分：引用论文清单

列出 [A]~[F] 六篇论文的完整元信息：

```text
- [Tag] 作者 (年份). "标题." 发表刊物/预印本平台. 标识符. 检索词: {检索策略}
```

---

## 阶段 2：REFCHECKER_REPAIR_LOG

对 ORIGINAL_REPORT 中的引用和 claim-citation pair 做核查。

### 必须调用

- 对 [A]~[F] 逐条调用 refchecker 的 `verify_citation`。
- 基于已阅读的 PDF/全文检查 claim 是否被引用位置支持。

### 输出格式

JSONL 代码块。每行一个 JSON 对象：

```jsonl
{"item_id":"ref_A","item_type":"reference_metadata","citation_tag":"A","refchecker_verified":"yes_or_no","issue_type":"none_or_metadata_error","issue_summary":"...","repair_action":"none_or_correct_metadata"}
{"item_id":"claim_01","item_type":"claim_citation_pair","citation_tag":"A","refchecker_verified":"yes_or_no","issue_type":"none_or_overclaim_or_miscitation_or_unsupported","issue_summary":"...","repair_action":"none_or_weaken_claim_or_remove_claim"}
```

---

## 阶段 3：生成修复后报告 REPAIRED_REPORT

基于 REPAIR_LOG 修复 ORIGINAL_REPORT：
- 元数据错误 → 修正引用清单
- claim 超出引用支持 → 弱化或删除
- 不要新增未经检查的强 claim

---

## 最终输出格式

严格按以下四个顶层标题输出：

# ORIGINAL_REPORT

{阶段 1 初稿}

# REFCHECKER_REPAIR_LOG

```jsonl
{阶段 2 JSONL}
```

# REPAIRED_REPORT

{阶段 3 修复后报告}

# RUN_SUMMARY

```json
{"case_id":"demo","run_id":"1","num_references_checked":6,"num_claims":0,"num_issues_found":0,"num_revisions_made":0}
```

除上述四个顶层标题外，不要输出额外解释。
PROMPTEOF

echo "✅ Prompt 已生成: $PROMPT_FILE"

# ── 4. 运行 Agent ─────────────────────────────────────────────────
echo ""
echo "→ 启动 OpenClaw Agent（超时: ${TIMEOUT}s）..."
echo "  提示：Agent 需要时间阅读 PDF、检索论文、生成报告、核查引用"
echo ""

RAW_OUTPUT="$OUTPUT_DIR/output.raw.txt"
RUN_LOG="$OUTPUT_DIR/run.log"

{
  echo "=== START $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
  echo "session_key=$SESSION_KEY"
  echo "topic=$TOPIC"
  echo "pdf=$PDF_NAME"
  set +e
  openclaw --profile "$PROFILE" agent --local \
    --timeout "$TIMEOUT" \
    --thinking "$THINKING" \
    --session-key "$SESSION_KEY" \
    --message "$(cat "$PROMPT_FILE")" \
    > "$RAW_OUTPUT" 2>"$OUTPUT_DIR/stderr.log"
  STATUS="$?"
  set -e
  echo "command_status=$STATUS"
  for marker in '^# ORIGINAL_REPORT' '^# REFCHECKER_REPAIR_LOG' '^# REPAIRED_REPORT' '^# RUN_SUMMARY'; do
    if grep -Eq "$marker" "$RAW_OUTPUT"; then
      echo "✅ 找到 $marker"
    else
      echo "❌ 缺少 $marker"
    fi
  done
  echo "=== END $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
} | tee "$RUN_LOG"

echo ""
echo "============================================"
echo " 运行完成"
echo "============================================"
echo " 输出目录: $OUTPUT_DIR"
echo "   prompt.md         → 发送的 prompt"
echo "   output.raw.txt    → Agent 完整输出"
echo "   run.log           → 运行日志"
echo "   stderr.log        → 错误日志"
