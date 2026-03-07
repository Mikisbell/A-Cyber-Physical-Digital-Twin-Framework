#!/usr/bin/env bash
# tools/setup_dependencies.sh — Install Gentleman Programming ecosystem
# ======================================================================
# Installs the required external tools for the Belico Stack EIU.
# Run this ONCE after cloning the repository.
#
# Usage:
#   bash tools/setup_dependencies.sh          # interactive
#   bash tools/setup_dependencies.sh --all    # install everything
#   bash tools/setup_dependencies.sh --check  # only check status
#   bash tools/setup_dependencies.sh --update # update all to latest
#   bash tools/setup_dependencies.sh --lock   # save current versions to lockfile

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# ── Component registry ───────────────────────────────────────────────
# Each component: name | brew formula | gh repo | required?
COMPONENTS=(
  "engram|gentleman-programming/tap/engram|Gentleman-Programming/engram|required"
  "gentle-ai|gentleman-programming/tap/gentle-ai|Gentleman-Programming/gentle-ai|required"
  "gga|gentleman-programming/tap/gga|Gentleman-Programming/gentleman-guardian-angel|required"
  "agent-teams-lite|-|Gentleman-Programming/agent-teams-lite|required"
  "Gentleman-Skills|-|Gentleman-Programming/Gentleman-Skills|optional"
)

# ── Helpers ───────────────────────────────────────────────────────────

print_header() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  Belico Stack — Dependency Installer${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

check_command() {
  command -v "$1" &>/dev/null
}

check_component() {
  local name="$1" brew_formula="$2" gh_repo="$3" required="$4"
  local status=""

  case "$name" in
    engram|gentle-ai|gga)
      if check_command "$name"; then
        local ver
        ver=$("$name" version 2>/dev/null || "$name" --version 2>/dev/null || echo "installed")
        status="${GREEN}[OK]${NC} $name ($ver)"
      else
        if [[ "$required" == "required" ]]; then
          status="${RED}[MISSING]${NC} $name (REQUIRED)"
        else
          status="${YELLOW}[MISSING]${NC} $name (optional)"
        fi
      fi
      ;;
    agent-teams-lite|Gentleman-Skills)
      if [[ -d "$ROOT/.agents/$name" ]] && [[ -n "$(ls -A "$ROOT/.agents/$name" 2>/dev/null)" ]]; then
        status="${GREEN}[OK]${NC} $name (.agents/$name/)"
      else
        if [[ "$required" == "required" ]]; then
          status="${RED}[MISSING]${NC} $name (REQUIRED)"
        else
          status="${YELLOW}[MISSING]${NC} $name (optional)"
        fi
      fi
      ;;
  esac

  echo -e "  $status"
}

install_component() {
  local name="$1" brew_formula="$2" gh_repo="$3"

  echo -e "\n${CYAN}Installing $name...${NC}"

  case "$name" in
    engram|gentle-ai|gga)
      if check_command brew; then
        brew install "$brew_formula" 2>/dev/null || {
          echo -e "${YELLOW}  Brew failed. Trying binary install...${NC}"
          install_from_release "$name" "$gh_repo"
        }
      else
        install_from_release "$name" "$gh_repo"
      fi
      ;;
    agent-teams-lite|Gentleman-Skills)
      mkdir -p "$ROOT/.agents"
      if [[ -d "$ROOT/.agents/$name" ]]; then
        echo "  Updating $name..."
        cd "$ROOT/.agents/$name" && git pull --ff-only 2>/dev/null || true
        cd "$ROOT"
      else
        echo "  Cloning $gh_repo..."
        git clone "https://github.com/$gh_repo.git" "$ROOT/.agents/$name"
      fi
      ;;
  esac

  echo -e "${GREEN}  Done.${NC}"
}

install_from_release() {
  local name="$1" gh_repo="$2"
  local os arch
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"
  [[ "$arch" == "x86_64" ]] && arch="amd64"
  [[ "$arch" == "aarch64" ]] && arch="arm64"

  echo "  Downloading latest release for ${os}/${arch}..."

  local tmpdir
  tmpdir="$(mktemp -d)"
  if gh release download --repo "$gh_repo" --pattern "*${os}_${arch}*" --dir "$tmpdir" 2>/dev/null; then
    local archive
    archive="$(ls "$tmpdir"/* 2>/dev/null | head -1)"
    if [[ "$archive" == *.tar.gz ]]; then
      tar xzf "$archive" -C "$tmpdir"
    elif [[ "$archive" == *.zip ]]; then
      unzip -qo "$archive" -d "$tmpdir"
    fi
    local binary
    binary="$(find "$tmpdir" -name "$name" -type f -perm -u+x 2>/dev/null | head -1)"
    if [[ -z "$binary" ]]; then
      binary="$(find "$tmpdir" -name "$name" -type f 2>/dev/null | head -1)"
      [[ -n "$binary" ]] && chmod +x "$binary"
    fi
    if [[ -n "$binary" ]]; then
      sudo cp "$binary" /usr/local/bin/ 2>/dev/null || cp "$binary" "$HOME/.local/bin/" 2>/dev/null || {
        echo -e "${RED}  Could not install binary. Copy manually: $binary${NC}"
      }
    fi
  else
    echo -e "${RED}  Failed to download. Install manually from: https://github.com/$gh_repo/releases${NC}"
  fi
  rm -rf "$tmpdir"
}

setup_engram() {
  if check_command engram; then
    echo -e "\n${CYAN}Configuring Engram for Claude Code...${NC}"
    engram setup claude-code 2>/dev/null || engram setup 2>/dev/null || {
      echo -e "${YELLOW}  Auto-setup failed. Configure manually: engram setup${NC}"
    }
  fi
}

# ── Update ─────────────────────────────────────────────────────────────

get_version() {
  local name="$1"
  case "$name" in
    engram|gentle-ai|gga)
      if check_command "$name"; then
        "$name" version 2>/dev/null || "$name" --version 2>/dev/null || echo "unknown"
      else
        echo "not-installed"
      fi
      ;;
    agent-teams-lite|Gentleman-Skills)
      if [[ -d "$ROOT/.agents/$name/.git" ]]; then
        git -C "$ROOT/.agents/$name" rev-parse --short HEAD 2>/dev/null || echo "unknown"
      else
        echo "not-installed"
      fi
      ;;
  esac
}

update_component() {
  local name="$1" brew_formula="$2" gh_repo="$3"
  local before after

  before="$(get_version "$name")"

  case "$name" in
    engram|gentle-ai|gga)
      if ! check_command "$name"; then
        echo -e "  ${YELLOW}[SKIP]${NC} $name — not installed"
        return
      fi
      if check_command brew && brew list "$brew_formula" &>/dev/null; then
        brew upgrade "$brew_formula" 2>/dev/null || true
      else
        install_from_release "$name" "$gh_repo"
      fi
      ;;
    agent-teams-lite|Gentleman-Skills)
      if [[ -d "$ROOT/.agents/$name/.git" ]]; then
        git -C "$ROOT/.agents/$name" pull --ff-only 2>/dev/null || {
          echo -e "  ${YELLOW}[WARN]${NC} $name — pull failed (local changes?)"
          return
        }
      else
        echo -e "  ${YELLOW}[SKIP]${NC} $name — not installed"
        return
      fi
      ;;
  esac

  after="$(get_version "$name")"
  if [[ "$before" == "$after" ]]; then
    echo -e "  ${GREEN}[OK]${NC} $name — up to date ($after)"
  else
    echo -e "  ${GREEN}[UPDATED]${NC} $name — $before → $after"
  fi
}

update_all() {
  print_header
  echo "  Updating all dependencies..."
  echo ""
  for comp in "${COMPONENTS[@]}"; do
    IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
    update_component "$name" "$brew_formula" "$gh_repo"
  done
  echo ""
  echo -e "${GREEN}  Update complete.${NC}"
  echo ""
  save_lockfile
}

# ── Lockfile ──────────────────────────────────────────────────────────

LOCKFILE="$ROOT/config/dependencies.lock"

save_lockfile() {
  mkdir -p "$(dirname "$LOCKFILE")"
  {
    echo "# Belico Stack — Dependency Versions"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# Re-lock: bash tools/setup_dependencies.sh --lock"
    echo ""
    for comp in "${COMPONENTS[@]}"; do
      IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
      local ver
      ver="$(get_version "$name")"
      # For git repos, also capture the remote URL and branch
      if [[ "$name" == "agent-teams-lite" || "$name" == "Gentleman-Skills" ]]; then
        local branch=""
        if [[ -d "$ROOT/.agents/$name/.git" ]]; then
          branch="$(git -C "$ROOT/.agents/$name" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")"
        fi
        echo "$name=$ver  # branch=$branch repo=$gh_repo"
      else
        echo "$name=$ver  # brew=$brew_formula repo=$gh_repo"
      fi
    done
  } > "$LOCKFILE"
  echo -e "  ${GREEN}Lockfile saved:${NC} config/dependencies.lock"
}

# ── Main ──────────────────────────────────────────────────────────────

main() {
  local mode="${1:-interactive}"
  print_header

  # Prerequisites
  if ! check_command git; then
    echo -e "${RED}ERROR: git is required. Install git first.${NC}"
    exit 1
  fi

  # Check mode
  if [[ "$mode" == "--check" ]]; then
    echo "  Dependency status:"
    echo ""
    for comp in "${COMPONENTS[@]}"; do
      IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
      check_component "$name" "$brew_formula" "$gh_repo" "$required"
    done
    echo ""
    # Check Python deps
    echo "  Python packages:"
    for pkg in yake yaml numpy scipy matplotlib; do
      if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}[OK]${NC} $pkg"
      else
        echo -e "  ${RED}[MISSING]${NC} $pkg — pip install $pkg"
      fi
    done
    echo ""
    return 0
  fi

  # Update mode
  if [[ "$mode" == "--update" ]]; then
    update_all
    return 0
  fi

  # Lock mode
  if [[ "$mode" == "--lock" ]]; then
    print_header
    save_lockfile
    echo ""
    return 0
  fi

  # Show status first
  echo "  Current status:"
  echo ""
  local missing_required=0
  for comp in "${COMPONENTS[@]}"; do
    IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
    check_component "$name" "$brew_formula" "$gh_repo" "$required"
    case "$name" in
      engram|gentle-ai|gga)
        if ! check_command "$name" && [[ "$required" == "required" ]]; then
          missing_required=$((missing_required + 1))
        fi
        ;;
      agent-teams-lite|Gentleman-Skills)
        if [[ ! -d "$ROOT/.agents/$name" ]] || [[ -z "$(ls -A "$ROOT/.agents/$name" 2>/dev/null)" ]]; then
          [[ "$required" == "required" ]] && missing_required=$((missing_required + 1))
        fi
        ;;
    esac
  done

  echo ""

  if [[ $missing_required -eq 0 && "$mode" != "--all" ]]; then
    echo -e "${GREEN}  All required dependencies are installed.${NC}"
    echo ""
    return 0
  fi

  # Install
  if [[ "$mode" == "--all" ]]; then
    for comp in "${COMPONENTS[@]}"; do
      IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
      install_component "$name" "$brew_formula" "$gh_repo"
    done
  else
    # Interactive: install only missing required, ask for optional
    for comp in "${COMPONENTS[@]}"; do
      IFS='|' read -r name brew_formula gh_repo required <<< "$comp"
      local installed=false
      case "$name" in
        engram|gentle-ai|gga) check_command "$name" && installed=true ;;
        *) [[ -d "$ROOT/.agents/$name" ]] && [[ -n "$(ls -A "$ROOT/.agents/$name" 2>/dev/null)" ]] && installed=true ;;
      esac

      if [[ "$installed" == "false" ]]; then
        if [[ "$required" == "required" ]]; then
          install_component "$name" "$brew_formula" "$gh_repo"
        else
          echo -en "\n  Install ${name}? (optional) [y/N]: "
          read -r ans
          [[ "$ans" =~ ^[yYsS] ]] && install_component "$name" "$brew_formula" "$gh_repo"
        fi
      fi
    done
  fi

  # Post-install: configure Engram
  setup_engram

  # Python dependencies
  echo -e "\n${CYAN}Installing Python dependencies...${NC}"
  if [[ -f "$ROOT/requirements.txt" ]]; then
    pip install -r "$ROOT/requirements.txt" 2>/dev/null || \
    pip3 install -r "$ROOT/requirements.txt" 2>/dev/null || \
    python3 -m pip install -r "$ROOT/requirements.txt" 2>/dev/null || {
      echo -e "${YELLOW}  pip install failed. Run manually: pip install -r requirements.txt${NC}"
    }
  fi

  # Save lockfile with installed versions
  echo ""
  save_lockfile

  echo ""
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}  Setup complete. Run: claude${NC}"
  echo -e "${GREEN}  Then say: \"Engram conecto\"${NC}"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

main "$@"
