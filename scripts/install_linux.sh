#!/usr/bin/env bash
set -euo pipefail

APP_NAME="english-assessment"
MCP_NAME="english-kb"
DEFAULT_INSTALL_DIR="${HOME}/.local/share/${APP_NAME}"

usage() {
  cat <<'EOF'
Install English assessment KB MCP and skills on Linux.

Usage:
  scripts/install_linux.sh [options]

Options:
  --install-dir PATH       Install app files here. Default: ~/.local/share/english-assessment
  --agents LIST            Comma-separated agents: codex,claude,hermes,all
  --yes                    Non-interactive mode. Uses --agents or defaults to all.
  --skip-mcp-config        Copy app/skills but do not update agent MCP config.
  -h, --help               Show help.

Examples:
  scripts/install_linux.sh
  scripts/install_linux.sh --agents codex,claude
  scripts/install_linux.sh --yes --agents all

MCP config files:
  Codex:       ~/.codex/config.toml
  Claude Code: ~/.claude.json
  Hermes:      ~/.hermes/config.yaml
EOF
}

log() {
  printf '[install] %s\n' "$*"
}

die() {
  printf '[install] ERROR: %s\n' "$*" >&2
  exit 1
}

INSTALL_DIR="${DEFAULT_INSTALL_DIR}"
AGENTS=""
ASSUME_YES=0
SKIP_MCP_CONFIG=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir)
      INSTALL_DIR="${2:-}"
      [[ -n "${INSTALL_DIR}" ]] || die "--install-dir requires a path"
      shift 2
      ;;
    --agents)
      AGENTS="${2:-}"
      [[ -n "${AGENTS}" ]] || die "--agents requires a comma-separated list"
      shift 2
      ;;
    --yes)
      ASSUME_YES=1
      shift
      ;;
    --skip-mcp-config)
      SKIP_MCP_CONFIG=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
INSTALL_DIR="${INSTALL_DIR/#\~/${HOME}}"

require_file() {
  [[ -f "$1" ]] || die "Missing required file: $1"
}

require_dir() {
  [[ -d "$1" ]] || die "Missing required directory: $1"
}

normalize_agents() {
  local raw="$1"
  raw="${raw// /}"
  raw="${raw,,}"
  if [[ -z "$raw" || "$raw" == "all" ]]; then
    printf 'codex claude hermes'
    return
  fi
  local out=()
  IFS=',' read -r -a parts <<< "$raw"
  for agent in "${parts[@]}"; do
    case "$agent" in
      codex|claude|hermes) out+=("$agent") ;;
      *) die "Unsupported agent: ${agent}. Supported: codex, claude, hermes, all" ;;
    esac
  done
  printf '%s ' "${out[@]}"
}

prompt_agents() {
  if [[ -n "${AGENTS}" ]]; then
    normalize_agents "${AGENTS}"
    return
  fi
  if [[ "${ASSUME_YES}" -eq 1 ]]; then
    normalize_agents "all"
    return
  fi
  cat <<'EOF'
Choose AI agents to install skills for:
  1) Codex        (~/.codex/skills)
  2) Claude Code  (~/.claude/skills)
  3) Hermes Agent (~/.hermes/skills)
  4) All
EOF
  read -r -p "Enter choices, e.g. 1,2 or all [all]: " choice
  choice="${choice:-all}"
  choice="${choice// /}"
  choice="${choice,,}"
  case "$choice" in
    all|4) normalize_agents "all" ;;
    1) normalize_agents "codex" ;;
    2) normalize_agents "claude" ;;
    3) normalize_agents "hermes" ;;
    1,2|2,1) normalize_agents "codex,claude" ;;
    1,3|3,1) normalize_agents "codex,hermes" ;;
    2,3|3,2) normalize_agents "claude,hermes" ;;
    1,2,3|1,3,2|2,1,3|2,3,1|3,1,2|3,2,1) normalize_agents "all" ;;
    *) normalize_agents "$choice" ;;
  esac
}

copy_dir() {
  local src="$1"
  local dst="$2"
  rm -rf "$dst"
  mkdir -p "$(dirname "$dst")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$src/" "$dst/"
  else
    cp -a "$src" "$dst"
  fi
}

install_app_files() {
  require_file "${REPO_DIR}/knowledge_base.db"
  require_dir "${REPO_DIR}/kb_mcp"
  require_dir "${REPO_DIR}/skills"

  log "Installing app files to ${INSTALL_DIR}"
  mkdir -p "${INSTALL_DIR}"
  copy_dir "${REPO_DIR}/kb_mcp" "${INSTALL_DIR}/kb_mcp"
  copy_dir "${REPO_DIR}/skills" "${INSTALL_DIR}/skills"
  cp "${REPO_DIR}/knowledge_base.db" "${INSTALL_DIR}/knowledge_base.db"
  cp "${REPO_DIR}/kb_extract.py" "${INSTALL_DIR}/kb_extract.py" 2>/dev/null || true
  cp "${REPO_DIR}/README_MCP.md" "${INSTALL_DIR}/README_MCP.md" 2>/dev/null || true
}

install_python_env() {
  command -v python3 >/dev/null 2>&1 || die "python3 is required"
  log "Creating Python virtual environment"
  python3 -m venv "${INSTALL_DIR}/.venv"
  "${INSTALL_DIR}/.venv/bin/python" -m pip install --upgrade pip
  "${INSTALL_DIR}/.venv/bin/python" -m pip install mcp python-docx requests pyyaml
}

install_skills_for_agent() {
  local agent="$1"
  local skills_dir
  case "$agent" in
    codex) skills_dir="${HOME}/.codex/skills" ;;
    claude) skills_dir="${HOME}/.claude/skills" ;;
    hermes) skills_dir="${HOME}/.hermes/skills" ;;
    *) die "Unsupported agent: $agent" ;;
  esac
  log "Installing skills for ${agent}: ${skills_dir}"
  mkdir -p "$skills_dir"
  copy_dir "${INSTALL_DIR}/skills/english-assessment-planner" "${skills_dir}/english-assessment-planner"
  copy_dir "${INSTALL_DIR}/skills/english-assessment-producer" "${skills_dir}/english-assessment-producer"
}

mcp_python() {
  printf '%s/.venv/bin/python' "$INSTALL_DIR"
}

mcp_server() {
  printf '%s/kb_mcp/server.py' "$INSTALL_DIR"
}

mcp_db() {
  printf '%s/knowledge_base.db' "$INSTALL_DIR"
}

json_escape() {
  python3 - "$1" <<'PY'
import json, sys
print(json.dumps(sys.argv[1]))
PY
}

install_codex_mcp() {
  local config="${HOME}/.codex/config.toml"
  mkdir -p "$(dirname "$config")"
  log "Configuring Codex MCP: ${config}"
  python3 - "$config" "$(mcp_python)" "$(mcp_server)" "$(mcp_db)" <<'PY'
from pathlib import Path
import sys

config = Path(sys.argv[1])
python = sys.argv[2]
server = sys.argv[3]
db = sys.argv[4]
block = f'''[mcp_servers.english-kb]
command = "{python}"
args = ["{server}"]
[mcp_servers.english-kb.env]
ENGLISH_KB_DB_PATH = "{db}"
'''
text = config.read_text(encoding="utf-8") if config.exists() else ""
lines = text.splitlines()
out = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip() == "[mcp_servers.english-kb]":
        i += 1
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith("[") and stripped not in {"[mcp_servers.english-kb.env]"}:
                break
            i += 1
        continue
    out.append(line)
    i += 1
new_text = "\n".join(out).rstrip()
if new_text:
    new_text += "\n\n"
new_text += block
config.write_text(new_text, encoding="utf-8")
PY
}

install_claude_mcp() {
  local config="${HOME}/.claude.json"
  log "Configuring Claude Code MCP: ${config}"
  python3 - "$config" "$(mcp_python)" "$(mcp_server)" "$(mcp_db)" <<'PY'
from pathlib import Path
import json
import sys

config = Path(sys.argv[1])
python = sys.argv[2]
server = sys.argv[3]
db = sys.argv[4]
if config.exists():
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
else:
    data = {}
data.setdefault("mcpServers", {})
data["mcpServers"]["english-kb"] = {
    "command": python,
    "args": [server],
    "env": {"ENGLISH_KB_DB_PATH": db},
}
config.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

install_hermes_mcp() {
  local config="${HOME}/.hermes/config.yaml"
  mkdir -p "$(dirname "$config")"
  log "Configuring Hermes MCP: ${config}"
  "$(mcp_python)" - "$config" "$(mcp_python)" "$(mcp_server)" "$(mcp_db)" <<'PY'
from pathlib import Path
import sys
import yaml

config = Path(sys.argv[1])
python = sys.argv[2]
server = sys.argv[3]
db = sys.argv[4]
if config.exists():
    try:
        data = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        data = {}
else:
    data = {}
if not isinstance(data, dict):
    data = {}
data.setdefault("mcpServers", {})
data["mcpServers"]["english-kb"] = {
    "command": python,
    "args": [server],
    "env": {"ENGLISH_KB_DB_PATH": db},
}
config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
PY
}

install_mcp_for_agent() {
  local agent="$1"
  [[ "$SKIP_MCP_CONFIG" -eq 0 ]] || return
  case "$agent" in
    codex) install_codex_mcp ;;
    claude) install_claude_mcp ;;
    hermes) install_hermes_mcp ;;
  esac
}

verify_install() {
  log "Verifying MCP server can start"
  ENGLISH_KB_DB_PATH="$(mcp_db)" timeout 3 "$(mcp_python)" "$(mcp_server)" >/tmp/english-kb-mcp-verify.log 2>&1 || true
  if grep -q "KB database not found" /tmp/english-kb-mcp-verify.log 2>/dev/null; then
    cat /tmp/english-kb-mcp-verify.log >&2
    die "MCP server could not find knowledge_base.db"
  fi
}

main() {
  local selected_agents
  selected_agents="$(prompt_agents)"

  install_app_files
  install_python_env

  for agent in ${selected_agents}; do
    install_skills_for_agent "$agent"
    install_mcp_for_agent "$agent"
  done

  verify_install

  cat <<EOF

Installed successfully.

App files:
  ${INSTALL_DIR}

MCP server:
  command: $(mcp_python)
  args:    $(mcp_server)
  env:     ENGLISH_KB_DB_PATH=$(mcp_db)

Installed agents:
  ${selected_agents}

Restart your agent application after installation so it reloads MCP config and skills.
EOF
}

main "$@"
