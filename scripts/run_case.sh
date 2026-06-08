#!/usr/bin/env bash
#============================================================================
# run_case.sh — action memory 实验触发入口（v3 适配新目录结构）
#
# 用法：
#   在当前对话中 exec 调用。
#
#   步骤式运行（走一步记一步）：
#     bash scripts/run_case.sh --step fetch-papers  --case 001 --run 1
#     bash scripts/run_case.sh --step find-DEF     --case 001 --run 1
#     bash scripts/run_case.sh --step read-papers   --case 001 --run 1
#     bash scripts/run_case.sh --step write-note    --case 001 --run 1
#     bash scripts/run_case.sh --step finish        --case 001 --run 1
#
#   冷启动（前 3 个 case 的 Run 1）：
#     bash scripts/run_case.sh --step fetch-papers --case 001 --run 1 --cold
#
# 参数：
#   --case      必需。case 编号（001/002/003/004/005）
#   --run       必需。run 编号（1/2/3/4）
#   --step      必需。当前步骤：
#                  fetch-papers  — 读取 prompt，打开提供的 3 篇 PDF
#                  find-DEF      — 上网检索 D/E/F 论文
#                  fetch-DEF     — fetch D/E/F 论文并阅读
#                  read-papers   — 全部 6 篇读完
#                  write-note    — 生成研究笔记
#                  finish        — case_complete + recall audit
#   --cold      可选。传入则跳过检索（冷启动），否则 warm
#   --dry-run   可选。只打印不执行
#
# 输出：
#   每一步的结果自动 append 到 action_memory.jsonl
#   finish 步骤自动触发 recall audit 到 memory_record/run_X/case_XXX_X/
#============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "${SCRIPT_DIR}/.." && pwd)"

CASE=""
RUN=""
STEP=""
COLD=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --case)     CASE="$2";   shift 2 ;;
    --run)      RUN="$2";    shift 2 ;;
    --step)     STEP="$2";   shift 2 ;;
    --cold)     COLD=true;   shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    *) echo "❌ 未知参数: $1"; exit 1 ;;
  esac
done

if [[ -z "$CASE" || -z "$RUN" || -z "$STEP" ]]; then
  echo "❌ --case, --run, --step 都是必需的"
  echo "用法: bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers [--cold]"
  exit 1
fi

# ── 路径 ──────────────────────────────────────────────────────────────────
CASE_ID="case_${CASE}"
CASE_DIR="${WORKSPACE}/case_detail"
PROMPT_FILE="${CASE_DIR}/prompts/${CASE_ID}.md"
PAPER_DIR="${CASE_DIR}/papers/${CASE_ID}"
NOTE_DIR="${CASE_DIR}/notes"
MEM_RECORD_DIR="${WORKSPACE}/memory_record/run_${RUN}/${CASE_ID}_${RUN}"
APPEND="${SCRIPT_DIR}/append.py"
PRE_HOOK="${SCRIPT_DIR}/pre_action_hook.sh"
REPORT="${SCRIPT_DIR}/generate_recall_report.py"

mkdir -p "${NOTE_DIR}" "${MEM_RECORD_DIR}"

# ── 提取课题标题 ─────────────────────────────────────────────────────────
TOPIC=""
if [[ -f "$PROMPT_FILE" ]]; then
  TOPIC=$(awk '/^## 课题/{found=1; next} found && /^## /{exit} found{print}' "$PROMPT_FILE" \
           | head -3 | tr '\n' ' ' | sed 's/^ *//;s/ *$//')
fi
if [[ -z "$TOPIC" ]]; then
  case "$CASE" in
    001) TOPIC="Tool-augmented vs pure prompting for coding" ;;
    002) TOPIC="Model collapse under synthetic data training" ;;
    003) TOPIC="Protein-ligand binding affinity prediction" ;;
    004) TOPIC="MLLM visual understanding vs human" ;;
    005) TOPIC="AI coding agents vs junior developers" ;;
  esac
fi

# ── 检索开关 ──────────────────────────────────────────────────────────────
SKIP_RETRIEVE=false
if $COLD; then
  SKIP_RETRIEVE=true
fi

# ── Dry-run 预览 ─────────────────────────────────────────────────────────
if $DRY_RUN; then
  echo "════════════════════════════════════════════"
  echo " 🐱 ${CASE_ID} | Run ${RUN} | Step: ${STEP}"
  echo "════════════════════════════════════════════"
  echo "  课题:    ${TOPIC}"
  echo "  冷启动:  ${COLD} (skip_retrieve=${SKIP_RETRIEVE})"
  echo "  Prompt:  ${PROMPT_FILE}"
  echo "  论文:    ${PAPER_DIR}/"
  echo "  审计输出: ${MEM_RECORD_DIR}/"
  echo ""
  if $SKIP_RETRIEVE; then
    echo "  [⏭️] 跳过检索"
  else
    echo "  [🔍] 将检索 memory"
  fi
  echo ""
  echo "  本步骤操作："
  case "$STEP" in
    fetch-papers)
      echo "    - 读取 prompt"
      echo "    - 打开 ${PAPER_DIR}/ 下的 PDF (3篇)"
      echo "    - append.py 每条记录" ;;
    find-DEF)
      echo "    - 上网检索 D/E/F 论文"
      echo "    - 每篇 append.py" ;;
    fetch-DEF)
      echo "    - fetch D/E/F PDF 全文"
      echo "    - 阅读+提取关键数据"
      echo "    - 每篇 append.py" ;;
    read-papers)
      echo "    - 全部 6 篇读完"
      echo "    - 记录阅读完成状态" ;;
    write-note)
      echo "    - 生成研究笔记 → ${NOTE_DIR}/${CASE_ID}.md"
      echo "    - append.py write_note" ;;
    finish)
      echo "    - case_complete → append.py --case-complete"
      echo "    - recall audit → ${MEM_RECORD_DIR}/recall_audit.md" ;;
  esac
  exit 0
fi

# ── 实际执行 ─────────────────────────────────────────────────────────────

case "$STEP" in
  fetch-papers)
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 1/6: 获取提供的论文"
    echo "════════════════════════════════════════════"

    # 检索
    if ! $SKIP_RETRIEVE; then
      echo "[🔍] 检索 action memory..."
      bash "${PRE_HOOK}" \
        --action-type fetch_paper \
        --query "${TOPIC}" \
        --method summary_bm25 \
        --top-k 5 || true
    else
      echo "[⏭️] 冷启动，跳过检索"
    fi

    echo ""
    echo "[📄] Prompt: ${PROMPT_FILE}"
    echo "[📄] 论文目录: ${PAPER_DIR}/"
    echo ""
    echo "    提供的 3 篇 PDF:"
    for f in "${PAPER_DIR}"/*.pdf; do
      echo "      📎 $(basename "$f")"
    done
    echo ""
    echo "    请阅读 prompt，然后在对话中说 '开始读 [A]' 开始逐篇处理。"
    ;;

  find-DEF)
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 2/6: 检索 D/E/F"
    echo "════════════════════════════════════════════"

    if ! $SKIP_RETRIEVE; then
      echo "[🔍] 检索 action memory..."
      bash "${PRE_HOOK}" \
        --action-type search_paper \
        --query "${TOPIC} supplementary papers" \
        --method summary_bm25 \
        --top-k 5 || true
    fi

    echo ""
    echo "    请上网检索与本课题相关的 3 篇论文（优先 arXiv）。"
    echo "    每找到一篇 append.py 记录。"
    ;;

  fetch-DEF)
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 3/6: 获取 D/E/F 全文"
    echo "════════════════════════════════════════════"

    if ! $SKIP_RETRIEVE; then
      bash "${PRE_HOOK}" \
        --action-type fetch_paper \
        --query "${TOPIC} arXiv" \
        --method summary_bm25 \
        --top-k 3 || true
    fi

    echo ""
    echo "    请 fetch D/E/F 的 PDF，阅读并提取关键数据。"
    echo "    每篇完成后 append.py。"
    ;;

  read-papers)
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 4/6: 阅读完成"
    echo "════════════════════════════════════════════"

    python3 "${APPEND}" \
      --case-id "${CASE_ID}" \
      --step 4 \
      --action-type read_papers \
      --target "all 6 papers" \
      --success true \
      --outcome "6 篇论文阅读完成，准备好写研究笔记" \
      --summary-en "All 6 papers read, ready to write research note" \
      --keywords "complete, ${CASE_ID}"

    echo "    建议下一步: --step write-note"
    ;;

  write-note)
    NOTE_FILE="${NOTE_DIR}/${CASE_ID}.md"
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 5/6: 生成研究笔记"
    echo "════════════════════════════════════════════"

    echo "[💡] 请根据 6 篇论文撰写研究笔记。"
    echo "     输出文件: ${NOTE_FILE}"
    echo ""
    echo "     完成后在本对话中说 '笔记完成'，我帮你 finish。"
    ;;

  finish)
    echo "════════════════════════════════════════════"
    echo " 🐱 ${CASE_ID} | Run ${RUN} | Step 6/6: 完成"
    echo "════════════════════════════════════════════"

    # 最后检索
    if ! $SKIP_RETRIEVE; then
      bash "${PRE_HOOK}" \
        --action-type write_note \
        --query "${TOPIC} research note" \
        --method summary_bm25 \
        --top-k 5 || true
    fi

    # 先创建 memory_record 目录
    mkdir -p "${MEM_RECORD_DIR}"

    # 用 JSON 文件传递 _output_dir（让 append.py 把 recall audit 写对地方）
    TMP_JSON=$(mktemp /tmp/case_finish_XXXX.json)
    cat > "$TMP_JSON" << JSONEOF
{
  "case_id": "${CASE_ID}",
  "step": 99,
  "action_type": "write_note",
  "target": "case_complete",
  "success": true,
  "outcome": "${CASE_ID} Run ${RUN} 完成",
  "summary_en": "${CASE_ID} run ${RUN} complete",
  "keywords": ["complete", "${CASE_ID}", "run_${RUN}"],
  "_case_complete": true,
  "_output_dir": "${MEM_RECORD_DIR}"
}
JSONEOF

    python3 "${APPEND}" --json "$TMP_JSON"
    rm -f "$TMP_JSON"

    # 也复制一份研究笔记到 memory_record（若存在）
    if [[ -f "${NOTE_DIR}/${CASE_ID}.md" ]]; then
      cp "${NOTE_DIR}/${CASE_ID}.md" "${MEM_RECORD_DIR}/"
    fi

    echo ""
    echo "────────────────────────────────────────────"
    echo " ✅ ${CASE_ID} Run ${RUN} 完成"
    echo "    研究笔记: ${NOTE_DIR}/${CASE_ID}.md"
    echo "    召回审计: ${MEM_RECORD_DIR}/recall_audit.md"
    echo "────────────────────────────────────────────"
    ;;

  *)
    echo "❌ 未知步骤: ${STEP}"
    echo "可用步骤: fetch-papers / find-DEF / fetch-DEF / read-papers / write-note / finish"
    exit 1
    ;;
esac
