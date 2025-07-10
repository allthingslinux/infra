#!/bin/bash
# All Things Linux Infrastructure - Lefthook Setup Script
# This script installs and configures lefthook hooks for code quality

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
  local level="$1"
  shift
  local message="$*"

  case $level in
  "INFO")
    echo -e "${GREEN}[INFO]${NC} $message"
    ;;
  "WARN")
    echo -e "${YELLOW}[WARN]${NC} $message"
    ;;
  "ERROR")
    echo -e "${RED}[ERROR]${NC} $message"
    ;;
  "DEBUG")
    echo -e "${BLUE}[DEBUG]${NC} $message"
    ;;
  *)
    echo -e "$message"
    ;;
  esac
}

# Banner function
show_banner() {
  cat <<'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                   All Things Linux                            ║
║                 Lefthook Setup                               ║
║                                                               ║
║         Setting up automated code quality checks             ║
╚═══════════════════════════════════════════════════════════════╝
EOF
}

# Help function
show_help() {
  cat <<EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -f, --force     Force reinstall hooks even if already installed
    --uninstall     Remove lefthook hooks
    --update        Update hook dependencies

EXAMPLES:
    $0                 # Install lefthook hooks
    $0 --force         # Reinstall hooks
    $0 --uninstall     # Remove hooks
    $0 --update        # Update to latest versions

EOF
}

# Check if we're in a git repository
check_git_repo() {
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    log "ERROR" "Not in a git repository. Lefthook requires git."
    exit 1
  fi
  log "INFO" "Git repository detected."
}

# Check prerequisites
check_prerequisites() {
  log "INFO" "Checking prerequisites..."

  if ! command -v python3 >/dev/null 2>&1; then
    log "ERROR" "Python 3 is required but not installed."
    exit 1
  fi

  if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
    log "ERROR" "pip is required but not installed."
    exit 1
  fi

  log "INFO" "Prerequisites check passed."
}

# Install lefthook
install_lefthook() {
  log "INFO" "Installing lefthook and dependencies..."

  cd "$PROJECT_ROOT"

  # Install Python dependencies using uv (including lefthook)
  if command -v uv >/dev/null 2>&1; then
    uv sync
    log "INFO" "Dependencies installed successfully (including lefthook via uv)."
  else
    log "ERROR" "uv is required but not installed. Please install uv first."
    exit 1
  fi
}

# Setup lefthook hooks
setup_hooks() {
  local force="$1"

  cd "$PROJECT_ROOT"

  if [[ $force == "true" ]]; then
    log "INFO" "Force reinstalling lefthook hooks..."
    uv run lefthook uninstall || true
  fi

  # Check if hooks are already installed
  if [[ -f ".git/hooks/pre-commit" ]] && [[ $force != "true" ]]; then
    log "INFO" "Lefthook hooks already installed."
  else
    log "INFO" "Installing lefthook hooks..."
    uv run lefthook install
    log "INFO" "Lefthook hooks installed successfully!"
  fi

  # Verify installation
  if [[ -f ".lefthook.yml" ]]; then
    log "INFO" "Lefthook configuration found."
  else
    log "ERROR" "Lefthook configuration (.lefthook.yml) not found."
    exit 1
  fi

  log "INFO" "Running initial hook validation..."
  if uv run lefthook run pre-commit --all-files; then
    log "INFO" "✅ All hooks passed initial validation!"
  else
    log "WARN" "⚠️  Some hooks failed. This is normal on first run."
    log "INFO" "Hooks will run automatically on future commits."
  fi
}

# Update hooks
update_hooks() {
  log "INFO" "Updating lefthook hooks..."

  cd "$PROJECT_ROOT"

  # Update dependencies
  if command -v uv >/dev/null 2>&1; then
    uv sync
  fi

  # Reinstall hooks with latest configuration
  uv run lefthook uninstall || true
  uv run lefthook install
  uv run lefthook run pre-commit --all-files || true

  log "INFO" "Hooks updated successfully!"
}

# Uninstall hooks
uninstall_hooks() {
  log "INFO" "Uninstalling lefthook hooks..."

  cd "$PROJECT_ROOT"

  # Uninstall using uv run lefthook
  if command -v uv >/dev/null 2>&1; then
    uv run lefthook uninstall || true
    log "INFO" "Lefthook hooks uninstalled."
  else
    log "WARN" "uv not found. Cannot uninstall lefthook hooks."
  fi

  # Clean up git hooks directory
  if [[ -d ".git/hooks" ]]; then
    find .git/hooks -name "pre-commit*" -delete || true
    find .git/hooks -name "commit-msg*" -delete || true
    find .git/hooks -name "pre-push*" -delete || true
  fi

  log "INFO" "Cleanup completed."
}

# Main function
main() {
  show_banner

  # Default values
  local force="false"
  local uninstall="false"
  local update="false"

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
      show_help
      exit 0
      ;;
    -f | --force)
      force="true"
      shift
      ;;
    --uninstall)
      uninstall="true"
      shift
      ;;
    --update)
      update="true"
      shift
      ;;
    *)
      log "ERROR" "Unknown argument: $1"
      show_help
      exit 1
      ;;
    esac
  done

  # Run checks
  check_git_repo
  check_prerequisites

  if [[ $uninstall == "true" ]]; then
    uninstall_hooks
    exit 0
  fi

  if [[ $update == "true" ]]; then
    update_hooks
    exit 0
  fi

  # Install dependencies and setup hooks
  install_lefthook
  setup_hooks "$force"

  log "INFO" "🎉 Lefthook setup complete!"
  log "INFO" ""
  log "INFO" "Next steps:"
  log "INFO" "- Hooks will run automatically on every commit"
  log "INFO" "- Run 'uv run lefthook run pre-commit --all-files' to check all files"
  log "INFO" "- Run 'uv run lefthook run <hook-name>' to run specific hooks"
  log "INFO" "- Use 'git commit --no-verify' to skip hooks (not recommended)"
}

# Execute main function with all arguments
main "$@"
