#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="${MAIN_MEMORY_RUN_ROOT:-$ROOT_DIR/runs/main_memory}"
TARGET_CONDITION="${MAIN_MEMORY_CONDITION:-memory_on}"
CASE_PAPER_DIR="$ROOT_DIR/case paper"
BASE_CONFIG="${BASE_OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BASE_AUTH="${BASE_OPENCLAW_AUTH:-$HOME/.openclaw/agents/main/agent/auth-profiles.json}"
SKILL_DIR="$ROOT_DIR/citation-standard"
ARXIV_MCP_WRAPPER="$ROOT_DIR/evaluation/pre_experiments/scripts/openclaw_arxiv_mcp_safe.py"
THINKING_LEVEL="${EXPERIMENT_THINKING:-high}"
ARXIV_MCP_PYTHON="${ARXIV_MCP_PYTHON:-}"
REFCHECKER_MCP_COMMAND="${REFCHECKER_MCP_COMMAND:-}"
BASE_BRAVE_PLUGIN_DIR=""

if [[ -d "$HOME/.openclaw/npm/projects" ]]; then
  BASE_BRAVE_PLUGIN_DIR="$(find "$HOME/.openclaw/npm/projects" -maxdepth 1 -type d -name 'openclaw-brave-plugin-*' | sort | head -n 1 || true)"
fi

if [[ -z "$ARXIV_MCP_PYTHON" ]]; then
  for candidate in \
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
    /usr/local/bin/python3 \
    python3; do
    if "$candidate" -c 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec("arxiv_mcp_server") else 1)' >/dev/null 2>&1; then
      ARXIV_MCP_PYTHON="$candidate"
      break
    fi
  done
fi

if [[ -z "$ARXIV_MCP_PYTHON" ]]; then
  echo "Could not find a Python interpreter that can import arxiv_mcp_server." >&2
  echo "Set ARXIV_MCP_PYTHON=/path/to/python3 and rerun this script." >&2
  exit 1
fi

if [[ -z "$REFCHECKER_MCP_COMMAND" ]]; then
  for candidate in \
    /Library/Frameworks/Python.framework/Versions/3.13/bin/mcp-refchecker \
    /usr/local/bin/mcp-refchecker \
    mcp-refchecker; do
    if command -v "$candidate" >/dev/null 2>&1; then
      REFCHECKER_MCP_COMMAND="$candidate"
      break
    fi
  done
fi

if [[ -z "$REFCHECKER_MCP_COMMAND" ]]; then
  echo "Could not find the mcp-refchecker console script." >&2
  echo "Set REFCHECKER_MCP_COMMAND=/path/to/mcp-refchecker and rerun this script." >&2
  exit 1
fi

[[ -d "$RUN_ROOT" ]] || { echo "Run root does not exist: $RUN_ROOT" >&2; exit 1; }
[[ -f "$BASE_CONFIG" ]] || { echo "Base OpenClaw config not found: $BASE_CONFIG" >&2; exit 1; }
[[ -d "$CASE_PAPER_DIR" ]] || { echo "Case paper directory not found: $CASE_PAPER_DIR" >&2; exit 1; }
[[ -d "$SKILL_DIR" ]] || { echo "citation-standard skill directory not found: $SKILL_DIR" >&2; exit 1; }
[[ -f "$ARXIV_MCP_WRAPPER" ]] || { echo "arxiv MCP wrapper not found: $ARXIV_MCP_WRAPPER" >&2; exit 1; }

requested_profile() {
  local candidate="$1"
  local requested

  if [[ "$#" -eq 1 ]]; then
    return 0
  fi

  shift
  for requested in "$@"; do
    if [[ "$candidate" == "$requested" ]]; then
      return 0
    fi
  done

  return 1
}

prepared_profiles_file="$(mktemp "${TMPDIR:-/tmp}/main_memory_profiles.XXXXXX")"
trap 'rm -f "$prepared_profiles_file"' EXIT

if [[ "$TARGET_CONDITION" == "memory_on" ]]; then
  manifest_root="$RUN_ROOT/M1_memory_on"
else
  manifest_root="$RUN_ROOT"
fi

while IFS= read -r manifest; do
  eval "$(
    python3 - "$manifest" <<'PY'
import json
import shlex
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for key in [
    "openclaw_profile",
    "condition",
    "case_id",
    "openclaw_workspace_dir",
]:
    print(f"{key}={shlex.quote(str(data[key]))}")
PY
  )"

  profile="$openclaw_profile"
  if [[ "$TARGET_CONDITION" != "all" && "$condition" != "$TARGET_CONDITION" ]]; then
    continue
  fi
  if ! requested_profile "$profile" "$@"; then
    continue
  fi
  if grep -qx "$profile" "$prepared_profiles_file"; then
    continue
  fi
  printf '%s\n' "$profile" >> "$prepared_profiles_file"

  case_num="${case_id#C}"
  state_dir="$HOME/.openclaw-$profile"
  config_file="$state_dir/openclaw.json"
  workspace_dir="$openclaw_workspace_dir"
  arxiv_storage_dir="$workspace_dir/arxiv_mcp_papers"
  auth_dir="$state_dir/agents/main/agent"
  auth_file="$auth_dir/auth-profiles.json"
  profile_has_qqbot="false"
  if [[ -d "$state_dir/npm/projects" ]] && find "$state_dir/npm/projects" -maxdepth 1 -type d -name 'openclaw-qqbot-*' | grep -q .; then
    profile_has_qqbot="true"
  fi

  mkdir -p "$state_dir" "$workspace_dir" "$arxiv_storage_dir" "$auth_dir" "$state_dir/npm/projects"

  python3 - "$BASE_CONFIG" "$config_file" "$workspace_dir" "$arxiv_storage_dir" "$THINKING_LEVEL" "$ARXIV_MCP_PYTHON" "$ARXIV_MCP_WRAPPER" "$REFCHECKER_MCP_COMMAND" "$condition" "$profile_has_qqbot" <<'PY'
import json
import sys
from pathlib import Path

(
    src,
    dst,
    workspace_dir,
    arxiv_storage_dir,
    thinking_level,
    arxiv_mcp_python,
    arxiv_mcp_wrapper,
    refchecker_mcp_command,
    condition,
    profile_has_qqbot,
) = sys.argv[1:11]
profile_has_qqbot = profile_has_qqbot == "true"
memory_enabled = condition == "memory_on"

config = json.loads(Path(src).read_text(encoding="utf-8"))

base_servers = (config.get("mcp") or {}).get("servers") or {}
arxiv = dict(base_servers.get("arxiv") or {})
if not arxiv:
    raise SystemExit("Base config does not define mcp.servers.arxiv")
arxiv["command"] = arxiv_mcp_python
arxiv["args"] = [
    arxiv_mcp_wrapper,
    "--storage-path",
    arxiv_storage_dir,
]
arxiv_env = dict(arxiv.get("env") or {})
arxiv_env["PYTHONUNBUFFERED"] = "1"
arxiv_env.setdefault("NO_PROXY", "arxiv.org,export.arxiv.org,localhost,127.0.0.1")
arxiv_env.setdefault("ARXIV_MCP_EXPORT_TIMEOUT", "10")
arxiv_env.setdefault("ARXIV_MCP_ABS_TIMEOUT", "15")
arxiv_env.setdefault("ARXIV_MCP_PDF_TIMEOUT", "60")
arxiv_env.setdefault("ARXIV_MCP_DELAY_SECONDS", "6")
arxiv_env.setdefault("ARXIV_MCP_NUM_RETRIES", "0")
arxiv_env.setdefault("ARXIV_MCP_CONTENT_CHAR_LIMIT", "35000")
arxiv["env"] = arxiv_env

refchecker = dict(base_servers.get("refchecker") or {})
refchecker["command"] = refchecker_mcp_command
refchecker["args"] = []
refchecker_env = dict(refchecker.get("env") or {})
refchecker_env["PYTHONUNBUFFERED"] = "1"
refchecker_env.setdefault("NO_PROXY", "arxiv.org,export.arxiv.org,localhost,127.0.0.1")
refchecker["env"] = refchecker_env

config.setdefault("mcp", {})["servers"] = {
    "arxiv": arxiv,
    "refchecker": refchecker,
}

skills = config.setdefault("skills", {})
entries = skills.setdefault("entries", {})
entries["pdf"] = {"enabled": True}
entries["citation-standard"] = {"enabled": True}

agents_defaults = config.setdefault("agents", {}).setdefault("defaults", {})
agents_defaults["workspace"] = workspace_dir
agents_defaults["thinkingDefault"] = thinking_level
agents_defaults["startupContext"] = {"enabled": False}
if memory_enabled:
    agents_defaults["memorySearch"] = {
        "enabled": True,
        "sources": ["memory"],
        "experimental": {"sessionMemory": False},
        "multimodal": {"enabled": False},
    }
else:
    agents_defaults["memorySearch"] = {
        "enabled": False,
        "sources": [],
        "experimental": {"sessionMemory": False},
        "multimodal": {"enabled": False},
    }

plugins_root = config.setdefault("plugins", {})
plugins = plugins_root.setdefault("entries", {})

plugins.setdefault("brave", {})["enabled"] = True
plugins.setdefault("deepseek", {})["enabled"] = True
plugins["duckduckgo"] = {"enabled": False}
if profile_has_qqbot:
    plugins["qqbot"] = {"enabled": False}
else:
    plugins.pop("qqbot", None)

if memory_enabled:
    active_memory = plugins.get("active-memory") or {}
    active_config = active_memory.get("config") or {}
    active_config.setdefault("enabled", True)
    active_config.setdefault("agents", ["main"])
    active_config.setdefault("allowedChatTypes", ["direct"])
    active_config.setdefault("queryMode", "full")
    active_config.setdefault("promptStyle", "balanced")
    active_config.setdefault("timeoutMs", 15000)
    active_config.setdefault("maxSummaryChars", 220)
    active_config.setdefault("persistTranscripts", False)
    active_config.setdefault("logging", True)
    plugins["active-memory"] = {"enabled": True, "config": active_config}
    plugins["memory-wiki"] = {"enabled": True}
    plugins.pop("memory-core", None)
    plugins_root["allow"] = ["brave", "active-memory", "memory-wiki"]
    plugins_root.setdefault("bundledDiscovery", "allowlist")
    slots = plugins_root.get("slots") or {}
    if slots.get("memory") == "none":
        slots.pop("memory", None)
    if slots:
        plugins_root["slots"] = slots
    else:
        plugins_root.pop("slots", None)
else:
    for plugin_name in ["active-memory", "memory-wiki", "memory-core"]:
        plugins[plugin_name] = {"enabled": False}
    plugins_root["allow"] = ["brave"]
    plugins_root.setdefault("slots", {})["memory"] = "none"

tools = config.setdefault("tools", {})
tools.setdefault("fs", {})["workspaceOnly"] = True
web = tools.setdefault("web", {})
search = web.setdefault("search", {})
search["enabled"] = True
search["provider"] = "brave"

Path(dst).write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

  if [[ -f "$BASE_AUTH" ]]; then
    cp "$BASE_AUTH" "$auth_file"
    chmod 600 "$auth_file"
  else
    echo "WARNING: base auth profile not found: $BASE_AUTH" >&2
  fi

  if [[ -n "$BASE_BRAVE_PLUGIN_DIR" && -d "$BASE_BRAVE_PLUGIN_DIR" ]]; then
    cp -R "$BASE_BRAVE_PLUGIN_DIR" "$state_dir/npm/projects/"
  else
    echo "WARNING: base Brave plugin install not found under ~/.openclaw/npm/projects" >&2
  fi

  if [[ "$condition" == "memory_on" ]]; then
    for n in 1 2 3 4 5; do
      input_dir="$workspace_dir/input_papers/case${n}"
      mkdir -p "$input_dir"
      cp "$CASE_PAPER_DIR/case${n}"/*.pdf "$input_dir/"
    done
    cat > "$workspace_dir/MEMORY.md" <<'EOF'
# Experiment Memory Boundary

Use the MEMORY_CONTEXT injected in each prompt as procedural caution only.
Do not cite memory. Scientific evidence must come from [A]-[F] source materials.
EOF
  else
    input_dir="$workspace_dir/input_papers/case${case_num}"
    mkdir -p "$input_dir"
    cp "$CASE_PAPER_DIR/case${case_num}"/*.pdf "$input_dir/"
  fi

  openclaw --profile "$profile" skills install "$SKILL_DIR" --as citation-standard --global --force >/dev/null

  if [[ "$condition" == "memory_on" ]]; then
    audit_dir="$RUN_ROOT/M1_memory_on/_profile_audit"
  else
    audit_dir="$(dirname "$manifest")"
  fi
  mkdir -p "$audit_dir"
  AUDIT_OUT_DIR="$audit_dir" bash "$ROOT_DIR/evaluation/pre_experiments/scripts/audit_openclaw_profile.sh" "$profile" >/dev/null

  echo "Prepared profile: $profile ($condition)"
done < <(find "$manifest_root" -name run_manifest.json | sort)

echo "Prepared OpenClaw profiles for main memory experiment."
