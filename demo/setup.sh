#!/usr/bin/env bash
# =============================================================================
# OpenClaw 科研 Agent 现场展示 — 一键环境配置
# =============================================================================
# 用法: bash demo/setup.sh
# 作用: 创建 openclaw-demo profile，配置 citation-standard + pdf + brave + arxiv + refchecker
#       memory OFF，只保留必要工具
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROFILE="openclaw-demo"
DEMO_WORKSPACE="$HOME/.openclaw-${PROFILE}/workspace"

echo "============================================"
echo " OpenClaw Demo 环境配置"
echo " Profile: ${PROFILE}"
echo "============================================"
echo ""

# ── 1. 检查 openclaw 是否已安装 ──────────────────────────────────
if ! command -v openclaw &>/dev/null; then
  echo "❌ 未找到 openclaw CLI，请先安装: https://docs.openclaw.ai/install"
  exit 1
fi
echo "✅ openclaw $(openclaw --version 2>/dev/null | head -1)"

# ── 2. 安装 citation-standard skill ──────────────────────────────
echo ""
echo "→ 安装 citation-standard skill..."
CITATION_DIR="$PROJECT_DIR/citation-standard"
if [[ -d "$CITATION_DIR" ]]; then
  openclaw skills install "$CITATION_DIR" --as citation-standard --force 2>&1 | tail -1
  echo "✅ citation-standard 已安装"
else
  echo "❌ 找不到 citation-standard 目录: $CITATION_DIR"
  exit 1
fi

# ── 3. 创建 demo profile ─────────────────────────────────────────
echo ""
echo "→ 创建 ${PROFILE} profile..."

PROFILE_DIR="$HOME/.openclaw-${PROFILE}"
CONFIG_FILE="$PROFILE_DIR/openclaw.json"
DEMO_WORKSPACE="$PROFILE_DIR/workspace"

mkdir -p "$PROFILE_DIR/workspace/input_papers"

# 复制 base config（或 last-good backup）
if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
  cp "$HOME/.openclaw/openclaw.json" "$CONFIG_FILE"
else
  cp "$HOME/.openclaw/openclaw.json.last-good" "$CONFIG_FILE"
fi

# ── 4. 配置: 启用所需工具，关闭 memory ────────────────────────────
echo ""
echo "→ 配置工具开关..."

OPENCLAW_DEMO_PYTHON="${OPENCLAW_DEMO_PYTHON:-}"
if [[ -z "$OPENCLAW_DEMO_PYTHON" ]]; then
  for candidate in \
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3" \
    "$(command -v python3)"; do
    if [[ -x "$candidate" ]] && "$candidate" - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if all(importlib.util.find_spec(m) for m in (
    "mcp", "arxiv_mcp_server", "mcp_refchecker", "arxiv", "httpx"
)) else 1)
PY
    then
      OPENCLAW_DEMO_PYTHON="$candidate"
      break
    fi
  done
fi

if [[ -z "$OPENCLAW_DEMO_PYTHON" ]]; then
  echo "❌ 找不到同时包含 mcp / arxiv_mcp_server / mcp_refchecker 的 Python。"
  echo "   可用方式: OPENCLAW_DEMO_PYTHON=/path/to/python3 bash demo/setup.sh"
  exit 1
fi

REFCHECKER_WRAPPER="$PROJECT_DIR/evaluation/pre_experiments/scripts/openclaw_refchecker_mcp_safe.py"

echo "  MCP Python: $OPENCLAW_DEMO_PYTHON"
echo "  Refchecker wrapper: $REFCHECKER_WRAPPER"
SEARCH_PROVIDER="${OPENCLAW_DEMO_SEARCH_PROVIDER:-brave}"
echo "  Web search provider: $SEARCH_PROVIDER"

if [[ "$SEARCH_PROVIDER" == "brave" ]]; then
  BRAVE_PLUGIN_PATH="${OPENCLAW_DEMO_BRAVE_PLUGIN_PATH:-$HOME/.openclaw/npm/node_modules/@openclaw/brave-plugin}"
  if [[ -d "$BRAVE_PLUGIN_PATH" ]]; then
    echo "→ 安装 Brave web_search provider 到 demo profile..."
    openclaw --profile "$PROFILE" plugins install "$BRAVE_PLUGIN_PATH" --force 2>&1 | tail -3
  else
    echo "⚠️  未找到本机 Brave plugin: $BRAVE_PLUGIN_PATH"
    echo "   回退到 bundled duckduckgo。可用 OPENCLAW_DEMO_BRAVE_PLUGIN_PATH 指定路径。"
    SEARCH_PROVIDER="duckduckgo"
  fi
fi

OPENCLAW_DEMO_PYTHON="$OPENCLAW_DEMO_PYTHON" \
REFCHECKER_WRAPPER="$REFCHECKER_WRAPPER" \
SEARCH_PROVIDER="$SEARCH_PROVIDER" \
CONFIG_FILE="$CONFIG_FILE" \
PROJECT_DIR="$PROJECT_DIR" \
DEMO_WORKSPACE="$DEMO_WORKSPACE" \
python3 - <<'PY'
import json
import os

config_file = os.environ["CONFIG_FILE"]
project_dir = os.environ["PROJECT_DIR"]
demo_workspace = os.environ["DEMO_WORKSPACE"]
mcp_python = os.environ["OPENCLAW_DEMO_PYTHON"]
refchecker_wrapper = os.environ["REFCHECKER_WRAPPER"]
search_provider = os.environ["SEARCH_PROVIDER"]

with open(config_file) as f:
    cfg = json.load(f)

for name in cfg.get('skills',{}).get('entries',{}):
    cfg['skills']['entries'][name]['enabled'] = (name in ('pdf', 'citation-standard'))

cfg['mcp']['servers'] = {k: v for k, v in cfg['mcp']['servers'].items() if k in ('arxiv', 'refchecker')}
# Use an absolute executable so OpenClaw does not accidentally pick Anaconda python3.
cfg['mcp']['servers']['refchecker'] = {
    'command': mcp_python,
    'args': [refchecker_wrapper],
    'env': {
        'MCP_REFCHECKER_LOG_LEVEL': 'WARNING',
        'NO_PROXY': 'arxiv.org,export.arxiv.org,localhost,127.0.0.1'
    }
}

# arxiv MCP → safe wrapper (handles network instability)
arxiv_wrapper = project_dir + '/evaluation/pre_experiments/scripts/openclaw_arxiv_mcp_safe.py'
arxiv_storage = demo_workspace + '/arxiv_papers'
cfg['mcp']['servers']['arxiv'] = {
    'command': mcp_python,
    'args': [arxiv_wrapper, '--storage-path', arxiv_storage],
    'env': {
        'PYTHONUNBUFFERED': '1',
        'ARXIV_MCP_LOG_LEVEL': 'WARNING',
        'NO_PROXY': 'arxiv.org,export.arxiv.org,localhost,127.0.0.1',
        'ARXIV_MCP_EXPORT_TIMEOUT': '10',
        'ARXIV_MCP_ABS_TIMEOUT': '15',
        'ARXIV_MCP_PDF_TIMEOUT': '60',
        'ARXIV_MCP_DELAY_SECONDS': '6',
        'ARXIV_MCP_NUM_RETRIES': '0',
        'ARXIV_MCP_CONTENT_CHAR_LIMIT': '35000'
    }
}

allow = []
for name, entry in cfg.get('plugins',{}).get('entries',{}).items():
    if name in ('active-memory', 'memory-wiki', 'memory-core', 'qqbot', 'openclaw-weixin'):
        entry['enabled'] = False
    elif name in ('deepseek', search_provider):
        entry['enabled'] = True
        allow.append(name)
    elif name == 'brave' and search_provider != 'brave':
        entry['enabled'] = False
cfg['plugins']['allow'] = allow
cfg['plugins']['bundledDiscovery'] = 'compat'
cfg['plugins'].pop('slots', None)

entries = cfg.get('plugins', {}).get('entries', {})
for stale_name in ('qqbot', 'openclaw-weixin', 'active-memory', 'memory-wiki', 'memory-core'):
    entries.pop(stale_name, None)
if search_provider != 'brave':
    entries.pop('brave', None)
if search_provider != 'duckduckgo':
    entries.pop('duckduckgo', None)
cfg.get('channels', {}).pop('openclaw-weixin', None)
cfg.get('channels', {}).pop('qqbot', None)

cfg.setdefault('tools', {}).setdefault('web', {}).setdefault('search', {})
cfg['tools']['web']['search']['provider'] = search_provider
cfg['tools']['web']['search']['enabled'] = True

cfg['agents']['defaults']['memorySearch'] = {
    'enabled': False, 'sources': [],
    'experimental': {'sessionMemory': False},
    'multimodal': {'enabled': False}
}
cfg['agents']['defaults']['workspace'] = demo_workspace

with open(config_file, 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print('✅ Profile 配置完成')
PY

# ── 5. 复制认证文件 ──────────────────────────────────────────────
echo ""
echo "→ 复制认证文件..."
mkdir -p "$PROFILE_DIR/agents/main/agent"
cp "$HOME/.openclaw/agents/main/agent/auth-profiles.json" "$PROFILE_DIR/agents/main/agent/" 2>/dev/null || true
cp "$HOME/.openclaw/agents/main/agent/models.json" "$PROFILE_DIR/agents/main/agent/" 2>/dev/null || true
cp -r "$HOME/.openclaw/agents/main/agent/plugins" "$PROFILE_DIR/agents/main/agent/" 2>/dev/null || true
echo "✅ 认证文件已复制"

# ── 6. 创建 workspace 目录结构 ───────────────────────────────────
mkdir -p "$DEMO_WORKSPACE/input_papers"

# ── 7. 验证配置 ──────────────────────────────────────────────────
echo ""
echo "→ 验证配置..."
if openclaw --profile "$PROFILE" config validate 2>&1 | grep -q "valid"; then
  echo "✅ ${PROFILE} profile 配置有效"
else
  echo "⚠️  配置可能有警告，但不影响运行"
fi

echo ""
echo "============================================"
echo " 环境配置完成！"
echo "============================================"
echo ""
echo " 启动方式:"
echo "   bash demo/run.sh --pdf /path/to/paper.pdf --topic \"研究课题\""
echo ""
echo " 或直接对话:"
echo "   openclaw --profile ${PROFILE}"
