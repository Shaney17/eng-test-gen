#!/usr/bin/env bash
set -euo pipefail

APP_NAME="english-assessment"
MCP_NAME="english-kb"
DEFAULT_INSTALL_DIR="${HOME}/.local/share/${APP_NAME}"
GITHUB_REPO="Shaney17/eng-test-gen"
DEFAULT_REF="${ENG_TEST_GEN_REF:-main}"
DEFAULT_DB_URL="${ENG_TEST_GEN_DB_URL:-}"

usage() {
  cat <<'EOF'
Install English assessment KB MCP and skills on Linux.

Usage:
  scripts/install_linux.sh [options]

Options:
  --install-dir PATH       Install app files here. Default: ~/.local/share/english-assessment
  --agents LIST            Comma-separated agents: codex,claude,hermes,all
  --ref REF                Git ref to download when running from curl. Default: main
  --db-url URL             Download knowledge_base.db from this URL.
  --yes                    Non-interactive mode. Requires --agents.
  --skip-mcp-config        Copy app/skills but do not update agent MCP config.
  -h, --help               Show help.

Examples:
  scripts/install_linux.sh
  scripts/install_linux.sh --agents codex,claude
  scripts/install_linux.sh --yes --agents all
  curl -fsSL https://github.com/Shaney17/eng-test-gen/raw/main/scripts/install_linux.sh | bash

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
REF="${DEFAULT_REF}"
DB_URL="${DEFAULT_DB_URL}"
SCRIPT_INPUT="${BASH_SOURCE[0]:-$0}"
REPO_DIR=""
TEMP_SOURCE_DIR=""

cleanup() {
  if [[ -n "${TEMP_SOURCE_DIR}" && -d "${TEMP_SOURCE_DIR}" ]]; then
    rm -rf "${TEMP_SOURCE_DIR}"
  fi
}
trap cleanup EXIT

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
    --ref)
      REF="${2:-}"
      [[ -n "${REF}" ]] || die "--ref requires a git ref"
      shift 2
      ;;
    --db-url)
      DB_URL="${2:-}"
      [[ -n "${DB_URL}" ]] || die "--db-url requires a URL"
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

INSTALL_DIR="${INSTALL_DIR/#\~/${HOME}}"
if [[ -z "${DB_URL}" ]]; then
  DB_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/${REF}/knowledge_base.db"
fi

require_file() {
  [[ -f "$1" ]] || die "Missing required file: $1"
}

require_dir() {
  [[ -d "$1" ]] || die "Missing required directory: $1"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "$1 is required"
}

lowercase() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

download_file() {
  local url="$1"
  local dst="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$dst"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$dst" "$url"
  else
    die "curl or wget is required to download files"
  fi
}

detect_local_repo() {
  local script_dir candidate
  if [[ -n "${SCRIPT_INPUT}" && -f "${SCRIPT_INPUT}" ]]; then
    script_dir="$(cd "$(dirname "${SCRIPT_INPUT}")" && pwd)"
    candidate="$(cd "${script_dir}/.." && pwd)"
    if [[ -d "${candidate}/kb_mcp" && -d "${candidate}/skills" ]]; then
      printf '%s' "$candidate"
      return
    fi
  fi

  if [[ -d "./kb_mcp" && -d "./skills" && -f "./scripts/install_linux.sh" ]]; then
    pwd
  fi
}

prepare_source_repo() {
  local local_repo archive
  local_repo="$(detect_local_repo)"
  if [[ -n "${local_repo}" ]]; then
    REPO_DIR="${local_repo}"
    log "Using local source: ${REPO_DIR}"
    return
  fi

  require_command tar
  TEMP_SOURCE_DIR="$(mktemp -d)"
  archive="${TEMP_SOURCE_DIR}/source.tar.gz"
  log "Downloading source from GitHub (${GITHUB_REPO}@${REF})"
  download_file "https://github.com/${GITHUB_REPO}/archive/${REF}.tar.gz" "$archive"
  tar -xzf "$archive" -C "${TEMP_SOURCE_DIR}"
  REPO_DIR="$(find "${TEMP_SOURCE_DIR}" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [[ -n "${REPO_DIR}" ]] || die "Could not unpack source archive"
}

install_database() {
  local dst="${INSTALL_DIR}/knowledge_base.db"
  if [[ -f "${REPO_DIR}/knowledge_base.db" ]]; then
    cp "${REPO_DIR}/knowledge_base.db" "$dst"
    return
  fi

  if [[ -f "$dst" ]]; then
    log "Using existing database: ${dst}"
    return
  fi

  log "Downloading knowledge_base.db"
  if ! download_file "$DB_URL" "$dst"; then
    rm -f "$dst"
    die "Could not download knowledge_base.db from ${DB_URL}. Provide --db-url or set ENG_TEST_GEN_DB_URL."
  fi
}

normalize_agents() {
  local raw="$1"
  raw="${raw// /}"
  raw="$(lowercase "$raw")"
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
    die "--yes requires --agents. Example: --yes --agents codex"
  fi
  [[ -r /dev/tty ]] || die "No interactive terminal available. Re-run with --agents codex, claude, hermes, or all."
  cat <<'EOF'
Choose AI agents to install skills for:
  1) Codex        (~/.codex/skills)
  2) Claude Code  (~/.claude/skills)
  3) Hermes Agent (~/.hermes/skills)
  4) All
EOF
  local choice
  while true; do
    printf 'Enter choices, e.g. 1,2 or all: ' > /dev/tty
    IFS= read -r choice < /dev/tty || die "Could not read agent selection"
    choice="${choice// /}"
    [[ -n "$choice" ]] && break
    printf '[install] Please choose at least one agent.\n' > /dev/tty
  done
  choice="${choice// /}"
  choice="$(lowercase "$choice")"
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
  require_dir "${REPO_DIR}/kb_mcp"
  require_dir "${REPO_DIR}/skills"

  log "Installing app files to ${INSTALL_DIR}"
  mkdir -p "${INSTALL_DIR}"
  copy_dir "${REPO_DIR}/kb_mcp" "${INSTALL_DIR}/kb_mcp"
  copy_dir "${REPO_DIR}/skills" "${INSTALL_DIR}/skills"
  install_database
  cp "${REPO_DIR}/kb_extract.py" "${INSTALL_DIR}/kb_extract.py" 2>/dev/null || true
  cp "${REPO_DIR}/README_MCP.md" "${INSTALL_DIR}/README_MCP.md" 2>/dev/null || true
}

run_apt_get() {
  if [[ "$(id -u)" -eq 0 ]]; then
    apt-get "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get "$@"
  else
    return 1
  fi
}

install_python_venv_package() {
  command -v apt-get >/dev/null 2>&1 || return 1

  local versioned_pkg
  versioned_pkg="$(python3 - <<'PY'
import sys
print(f"python{sys.version_info.major}.{sys.version_info.minor}-venv")
PY
)"

  log "Installing Python venv support with apt"
  run_apt_get update
  run_apt_get install -y "$versioned_pkg" || run_apt_get install -y python3-venv
}

ensure_debian_python_venv_package() {
  [[ -f /etc/debian_version ]] || return
  command -v apt-get >/dev/null 2>&1 || return
  command -v dpkg-query >/dev/null 2>&1 || return

  local versioned_pkg
  versioned_pkg="$(python3 - <<'PY'
import sys
print(f"python{sys.version_info.major}.{sys.version_info.minor}-venv")
PY
)"

  if dpkg-query -W -f='${Status}' "$versioned_pkg" 2>/dev/null | grep -q "install ok installed"; then
    return
  fi

  install_python_venv_package || die "python3 venv support is missing. Install it with: sudo apt-get update && sudo apt-get install -y ${versioned_pkg}"
}

ensure_python_venv() {
  local probe_dir
  probe_dir="$(mktemp -d)"
  if python3 -m venv "${probe_dir}/venv" >/tmp/english-assessment-venv-check.log 2>&1; then
    rm -rf "$probe_dir"
    return
  fi
  rm -rf "$probe_dir"

  if grep -Eqi "ensurepip|python3([.][0-9]+)?-venv" /tmp/english-assessment-venv-check.log 2>/dev/null; then
    install_python_venv_package || {
      cat /tmp/english-assessment-venv-check.log >&2
      die "python3 venv support is missing. Install it with: sudo apt-get update && sudo apt-get install -y python3-venv"
    }
    probe_dir="$(mktemp -d)"
    if python3 -m venv "${probe_dir}/venv" >/tmp/english-assessment-venv-check.log 2>&1; then
      rm -rf "$probe_dir"
      return
    fi
    rm -rf "$probe_dir"
  fi

  cat /tmp/english-assessment-venv-check.log >&2
  die "python3 -m venv failed"
}

install_python_env() {
  command -v python3 >/dev/null 2>&1 || die "python3 is required"
  ensure_debian_python_venv_package
  ensure_python_venv
  log "Creating Python virtual environment"
  rm -rf "${INSTALL_DIR}/.venv"
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

  prepare_source_repo
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
