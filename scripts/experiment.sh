#!/usr/bin/env bash
#============================================================================
# experiment.sh — 4 runs × 5 cases 实验编排脚本
#
# 这个脚本不在当前对话中执行，而是生成一份运行计划，
# 你可以在任何新对话中用 exec 执行具体的 run_case.sh 命令。
#
# 用法:
#   bash scripts/experiment.sh         # 打印完整实验计划
#   bash scripts/experiment.sh --run   # 生成所有 runs 的一键命令
#
# 实验设计:
#   Run 1: case_001/002/003 cold（无记忆检索），case_004/005 warm
#   Run 2: 全部 warm（记忆已有积累）
#   Run 3: 全部 warm（记忆更多积累）
#   Run 4: 全部 warm（最大记忆）
#============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "═══════════════════════════════════════════════════════════════"
echo " 🐱 实验计划: 4 Runs × 5 Cases"
echo "═══════════════════════════════════════════════════════════════"
echo ""

for RUN in 1 2 3 4; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " Run ${RUN}/4"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  for CASE in 001 002 003 004 005; do
    COLD_FLAG=""
    if [[ "$RUN" -eq 1 && "$CASE" =~ ^00[123]$ ]]; then
      COLD_FLAG="--cold"
    fi

    # 读取课题
    TOPIC=$(awk '/^## 课题/{found=1; next} found && /^## /{exit} found{print}' \
      "${SCRIPT_DIR}/../case_detail/prompts/case_${CASE}.md" 2>/dev/null \
      | head -3 | tr '\n' ' ' | sed 's/^ *//;s/ *$//')

    echo ""
    echo "  case_${CASE} | ${TOPIC:-课题未提取}"
    echo "  步骤命令:"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step fetch-papers  ${COLD_FLAG}"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step find-DEF      ${COLD_FLAG}"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step fetch-DEF     ${COLD_FLAG}"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step read-papers   ${COLD_FLAG}"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step write-note    ${COLD_FLAG}"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step finish        ${COLD_FLAG}"
    echo ""
    echo "  可先在当前对话中 dry-run 预览:"
    echo "    bash scripts/run_case.sh --case ${CASE} --run ${RUN} --step fetch-papers ${COLD_FLAG} --dry-run"
  done

  echo ""
done

echo "═══════════════════════════════════════════════════════════════"
echo " 📋 如何在新对话中触发"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  在新的 WebChat / Telegram / Signal 对话中，直接 exec:"
echo ""
echo '    bash ~/.openclaw/No_plan/scripts/run_case.sh --case 001 --run 1 --step fetch-papers --cold'
echo ""
echo "  注意: exec 时工作目录默认在 ~/.openclaw/No_plan，脚本会自己找路径。"
echo "        如果不行，先 cd 到工作目录:"
echo ""
echo "    cd ~/.openclaw/No_plan && bash scripts/run_case.sh --case 001 --run 1 --step fetch-papers --cold"
echo ""
echo "═══════════════════════════════════════════════════════════════"
