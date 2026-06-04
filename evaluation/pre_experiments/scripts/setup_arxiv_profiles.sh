#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RUN_ROOT="$ROOT_DIR/runs/pre_arxiv"
BASE_CONFIG="${BASE_OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
BASE_AUTH="${BASE_OPENCLAW_AUTH:-$HOME/.openclaw/agents/main/agent/auth-profiles.json}"
SKILL_DIR="$ROOT_DIR/citation-standard"
THINKING_LEVEL="${EXPERIMENT_THINKING:-high}"
BASE_BRAVE_PLUGIN_DIR="$(find "$HOME/.openclaw/npm/projects" -maxdepth 1 -type d -name 'openclaw-brave-plugin-*' | sort | head -n 1 || true)"
ARXIV_MCP_PYTHON="${ARXIV_MCP_PYTHON:-}"

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

if [[ ! -d "$RUN_ROOT" ]]; then
  echo "Run directory does not exist: $RUN_ROOT" >&2
  echo "Run prepare_arxiv_runs.sh first." >&2
  exit 1
fi

if [[ ! -f "$BASE_CONFIG" ]]; then
  echo "Base OpenClaw config not found: $BASE_CONFIG" >&2
  exit 1
fi

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "citation-standard skill directory not found: $SKILL_DIR" >&2
  exit 1
fi

profile_requested() {
  local candidate="$1"
  local requested_profile

  if [[ "$#" -eq 1 && "$REQUESTED_PROFILE_COUNT" -eq 0 ]]; then
    return 0
  fi

  shift
  for requested_profile in "$@"; do
    if [[ "$candidate" == "$requested_profile" ]]; then
      return 0
    fi
  done

  return 1
}

REQUESTED_PROFILE_COUNT="$#"

while IFS= read -r manifest; do
  profile="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["openclaw_profile"])' "$manifest")"
  if ! profile_requested "$profile" "$@"; then
    continue
  fi

  condition="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["condition"])' "$manifest")"
  state_dir="$HOME/.openclaw-$profile"
  config_file="$state_dir/openclaw.json"
  workspace_dir="$state_dir/workspace"
  auth_dir="$state_dir/agents/main/agent"
  auth_file="$auth_dir/auth-profiles.json"
  profile_has_qqbot="false"
  if find "$state_dir/npm/projects" -maxdepth 1 -type d -name 'openclaw-qqbot-*' | grep -q .; then
    profile_has_qqbot="true"
  fi

  mkdir -p "$state_dir"
  mkdir -p "$workspace_dir"
  mkdir -p "$auth_dir"
  mkdir -p "$state_dir/npm/projects"

  python3 - "$BASE_CONFIG" "$config_file" "$condition" "$workspace_dir" "$THINKING_LEVEL" "$ARXIV_MCP_PYTHON" "$profile_has_qqbot" <<'PY'
import json
import sys
from pathlib import Path

src, dst, condition, workspace_dir, thinking_level, arxiv_mcp_python, profile_has_qqbot = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7] == "true"
config = json.loads(Path(src).read_text())

base_servers = (config.get("mcp") or {}).get("servers") or {}
if condition == "arxiv_on":
    arxiv = dict(base_servers.get("arxiv") or {})
    if not arxiv:
        raise SystemExit("Base config does not define mcp.servers.arxiv")
    arxiv["command"] = arxiv_mcp_python
    arxiv["args"] = ["-m", "arxiv_mcp_server"]
    arxiv_env = dict(arxiv.get("env") or {})
    arxiv_env["PYTHONUNBUFFERED"] = "1"
    arxiv_env.setdefault("NO_PROXY", "arxiv.org,export.arxiv.org,localhost,127.0.0.1")
    arxiv["env"] = arxiv_env
    config.setdefault("mcp", {})["servers"] = {"arxiv": arxiv}
elif condition == "arxiv_off":
    config.setdefault("mcp", {})["servers"] = {}
else:
    raise SystemExit(f"Unknown condition: {condition}")

skills = config.setdefault("skills", {})
entries = skills.setdefault("entries", {})
entries["pdf"] = {"enabled": True}
entries["citation-standard"] = {"enabled": True}

agents_defaults = config.setdefault("agents", {}).setdefault("defaults", {})
agents_defaults["workspace"] = workspace_dir
agents_defaults["thinkingDefault"] = thinking_level
agents_defaults["startupContext"] = {"enabled": False}
agents_defaults["memorySearch"] = {
    "enabled": False,
    "sources": [],
    "experimental": {"sessionMemory": False},
    "multimodal": {"enabled": False},
}

plugins_root = config.setdefault("plugins", {})
plugins_root["allow"] = ["brave"]
plugins_root.setdefault("slots", {})["memory"] = "none"
plugins = plugins_root.setdefault("entries", {})
for plugin_name in [
    "active-memory",
    "memory-wiki",
    "memory-core",
    "duckduckgo",
]:
    plugins[plugin_name] = {"enabled": False}
if profile_has_qqbot:
    plugins["qqbot"] = {"enabled": False}
else:
    plugins.pop("qqbot", None)
plugins.setdefault("brave", {})["enabled"] = True

tools = config.setdefault("tools", {})
tools.setdefault("fs", {})["workspaceOnly"] = True
web = tools.setdefault("web", {})
search = web.setdefault("search", {})
search["enabled"] = True
search["provider"] = "brave"

Path(dst).write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
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

  # Install the local skill into this profile so `openclaw --profile ...` can see it.
  openclaw --profile "$profile" skills install "$SKILL_DIR" --as citation-standard --global --force >/dev/null

  audit_dir="$(dirname "$manifest")"
  AUDIT_OUT_DIR="$audit_dir" bash "$ROOT_DIR/evaluation/pre_experiments/scripts/audit_openclaw_profile.sh" "$profile" >/dev/null

  echo "Prepared profile: $profile ($condition)"
done < <(find "$RUN_ROOT" -name run_manifest.json | sort)

echo "Prepared OpenClaw profiles for arxiv MCP pre-experiment."
