#!/bin/bash
# pre_action_hook.sh v2 — 每次行动前先查 memory（支持 method 参数）
#
# 用法:
#   ./action_memory/pre_action_hook.sh \\
#     --action-type fetch_paper \\
#     --query "perspective benchmark MLLM" \\
#     --target "Paper A" \\
#     [--method summary_bm25] \\
#     [--top-k 5]
#
# 方法推荐:
#   bm25 (默认)      — 全文检索（中英混合），适合中英混合 query
#   summary_bm25     — 只查英文字段（推荐纯英文 query，得分最高）
#   hybrid           — 全文 + 英文摘要加权合并，更均衡
#
# 功能:
#   1. 检查配置 disabled / cold start
#   2. 检查当前 action_type 是否在 require_retrieve_before 列表
#   3. 调用 retrieve.py 检索相关记忆
#   4. 输出检索结果（可注入上下文用）
#   5. 记录检索日志到 retrieve_log.jsonl
#
# 退出码:
#   0 — 检索完成（无论是否有结果）
#   1 — 配置跳过（disabled / cold start）
#   2 — 不在 require_retrieve_before 中
#   3 — retrieve.py 运行失败

set -euo pipefail

MEMORY_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${MEMORY_DIR}/action_memory_config.json"
RETRIEVE_PY="${MEMORY_DIR}/retrieve.py"

# ── 解析参数 ─────────────────────────────────────
ACTION_TYPE=""
QUERY=""
TARGET=""
TOP_K=""
METHOD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --action-type) ACTION_TYPE="$2"; shift 2 ;;
        --query)       QUERY="$2";       shift 2 ;;
        --target)      TARGET="$2";      shift 2 ;;
        --method)      METHOD="$2";      shift 2 ;;
        --top-k)       TOP_K="$2";       shift 2 ;;
        *) echo "❌ 未知参数: $1"; exit 2 ;;
    esac
done

# ── 校验 ──────────────────────────────────────────
if [ -z "$ACTION_TYPE" ] || [ -z "$QUERY" ]; then
    echo "❌ 必须提供 --action-type 和 --query"
    exit 2
fi

# ── 读取配置 ─────────────────────────────────────
CHECK_ENABLE="$(python3 -c "
import json
c=json.load(open('${CONFIG_FILE}'))
print('true' if c.get('enable',True) else 'false')
")"
if [ "$CHECK_ENABLE" != "true" ]; then
    echo "⏭️  action memory disabled，跳过检索"
    exit 1
fi

# ── 检查 action_type 是否在 require_retrieve_before ──
CHECK_REQUIRED="$(python3 -c "
import json
c=json.load(open('${CONFIG_FILE}'))
required = c.get('require_retrieve_before',[])
print('true' if '${ACTION_TYPE}' in required else 'false')
")"
if [ "$CHECK_REQUIRED" != "true" ]; then
    echo "⏭️  action_type='${ACTION_TYPE}' 不在 require_retrieve_before 中，跳过检索"
    exit 2
fi

# ── 构建检索命令 ────────────────────────────────
TOP_K_CMD=""
if [ -n "$TOP_K" ]; then
    TOP_K_CMD="--top-k ${TOP_K}"
else
    TOP_K_CMD="--top-k $(python3 -c "
import json
c=json.load(open('${CONFIG_FILE}'))
print(c.get('default_top_k',3))
")"
fi

METHOD_CMD=""
if [ -n "$METHOD" ]; then
    METHOD_CMD="--method ${METHOD}"
fi

# ── 打印检索头部 ────────────────────────────────
echo "────────────────────────────────────────"
echo "🔍 行动前检索 | action: ${ACTION_TYPE}"
echo "   查询: ${QUERY}"
[ -n "$TARGET" ] && echo "   目标: ${TARGET}"
[ -n "$METHOD" ] && echo "   方法: ${METHOD}"
echo "────────────────────────────────────────"

# ── 执行检索 ────────────────────────────────────
python3 "${RETRIEVE_PY}" \
    --query "${QUERY}" \
    ${TOP_K_CMD} \
    ${METHOD_CMD} \
    --log-retrieve \
    --show-report 2>&1 || {
        echo "❌ retrieve.py 执行失败"
        exit 3
    }

echo "────────────────────────────────────────"
echo "✅ 检索完成，以上结果可注入推理上下文"
echo ""
