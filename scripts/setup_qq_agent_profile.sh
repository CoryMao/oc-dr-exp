#!/bin/bash
# Create qq-agent profile: citation-standard + pdf + brave + arxiv-mcp + refcheck, memory OFF
# After running this, use: openclaw --profile qq-agent

set -euo pipefail

PROFILE="qq-agent"
BASE_CONFIG="$HOME/.openclaw/openclaw.json"
PROFILE_DIR="$HOME/.openclaw-${PROFILE}"
PROFILE_CONFIG="$PROFILE_DIR/openclaw.json"
WORKSPACE_DIR="$PROFILE_DIR/workspace"

echo "==> Creating profile: ${PROFILE}"
mkdir -p "$PROFILE_DIR/workspace"

python3 -c "
import json, os, shutil

# Load base config
with open('$BASE_CONFIG') as f:
    cfg = json.load(f)

# ── 1. Skills: only pdf + citation-standard ───────────────────────
for name in cfg.get('skills', {}).get('entries', {}):
    cfg['skills']['entries'][name]['enabled'] = (name in ('pdf', 'citation-standard'))

# Ensure citation-standard entry exists (it may be global-only)
if 'citation-standard' not in cfg['skills']['entries']:
    cfg['skills']['entries']['citation-standard'] = {
        'enabled': True,
        'source': 'path',
        'spec': os.path.expanduser('$HOME/Desktop/Project2/citation-standard'),
        'slug': 'citation-standard'
    }

# ── 2. MCP servers: arxiv + refchecker (remove semantic-scholar) ─
cfg['mcp']['servers'] = {
    k: v for k, v in cfg['mcp']['servers'].items()
    if k in ('arxiv', 'refchecker')
}

# ── 3. Plugins: qqbot + brave + deepseek, DISABLE memory plugins ─
plugin_allow = []
for name, entry in cfg.get('plugins', {}).get('entries', {}).items():
    if name in ('active-memory', 'memory-wiki', 'duckduckgo'):
        entry['enabled'] = False
    elif name in ('qqbot', 'brave', 'deepseek'):
        entry['enabled'] = True
        plugin_allow.append(name)

cfg['plugins']['allow'] = plugin_allow
# Remove memory slot if present
cfg['plugins'].pop('slots', None)

# ── 4. Memory: fully OFF ─────────────────────────────────────────
if 'agents' not in cfg: cfg['agents'] = {}
if 'defaults' not in cfg['agents']: cfg['agents']['defaults'] = {}
cfg['agents']['defaults']['memorySearch'] = {
    'enabled': False,
    'sources': [],
    'experimental': {'sessionMemory': False},
    'multimodal': {'enabled': False}
}

# ── 5. Workspace ──────────────────────────────────────────────────
cfg['agents']['defaults']['workspace'] = '$PROFILE_DIR/workspace'

# ── 6. QQ bot: keep as-is (already enabled in base config) ────────
# No changes needed — qqbot plugin + channel stays enabled

# Write
with open('$PROFILE_CONFIG', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print('Profile config written.')
print(f'Skills enabled: pdf, citation-standard')
print(f'MCP enabled: arxiv, refchecker')
print(f'Plugins enabled: qqbot, brave, deepseek')
print(f'Memory: OFF')
print(f'QQ Bot: ON (appId={cfg[\"channels\"][\"qqbot\"][\"appId\"]})')
"

# ── 7. Create workspace README ────────────────────────────────────
cat > "$WORKSPACE_DIR/README.md" << 'EOF'
# QQ Agent Workspace

此 workspace 供 QQ Bot Agent 使用。

## 启用的工具
- **citation-standard**: 引用格式标准化
- **pdf**: PDF 阅读
- **arxiv-mcp**: arXiv 论文检索
- **refchecker**: 引用核查
- **brave search**: 网络搜索

## 禁用的功能
- **Memory**: 关闭，不跨会话记忆

## 使用方式
从 QQ 聊天框发送 prompt 即可触发 Agent。
EOF

echo ""
echo "=============================================="
echo "  Profile '${PROFILE}' 创建完成!"
echo "=============================================="
echo ""
echo "  启动 QQ Agent:"
echo "    openclaw --profile ${PROFILE}"
echo ""
echo "  或先 dry-run 测试:"
echo "    openclaw --profile ${PROFILE} --dry-run"
echo ""
echo "  配置位置: ${PROFILE_CONFIG}"
echo "  Workspace: ${WORKSPACE_DIR}"
