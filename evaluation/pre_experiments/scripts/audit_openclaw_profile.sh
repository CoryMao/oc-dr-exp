#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <profile-name>" >&2
  exit 1
fi

profile="$1"
out_dir="${AUDIT_OUT_DIR:-.}"
mkdir -p "$out_dir"

{
  echo "# OpenClaw Profile Audit"
  echo
  echo "profile: $profile"
  echo "timestamp_utc: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo
  echo "## Version"
  openclaw --profile "$profile" --version || true
  echo
  echo "## Config File"
  openclaw --profile "$profile" config file || true
  echo
  echo "## Config Validate"
  openclaw --profile "$profile" config validate || true
  echo
  echo "## MCP List"
  openclaw --profile "$profile" mcp list || true
  echo
  echo "## MCP Show"
  openclaw --profile "$profile" mcp show || true
  echo
  echo "## Skills Entries"
  openclaw --profile "$profile" config get skills.entries || true
  echo
  echo "## Skills List"
  openclaw --profile "$profile" skills list || true
  echo
  echo "## Skills Check"
  openclaw --profile "$profile" skills check || true
} > "$out_dir/openclaw_profile_audit.md" 2> "$out_dir/openclaw_profile_audit.stderr.log"

echo "Wrote profile audit to: $out_dir/openclaw_profile_audit.md"
