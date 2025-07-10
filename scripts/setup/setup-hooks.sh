#!/bin/bash
# All Things Linux Infrastructure - Pre-commit Setup Script
# This script installs and configures pre-commit hooks for code quality

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
║              Pre-commit Hooks Setup                          ║
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
    --uninstall     Remove pre-commit hooks
    --update        Update hook dependencies

EXAMPLES:
    $0                 # Install pre-commit hooks
    $0 --force         # Reinstall hooks
    $0 --uninstall     # Remove hooks
    $0 --update        # Update to latest versions

EOF
}

# Check if we're in a git repository
check_git_repo() {
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    log "ERROR" "Not in a git repository. Pre-commit requires git."
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

# Install pre-commit
install_precommit() {
  log "INFO" "Installing pre-commit and dependencies..."

  cd "$PROJECT_ROOT"

  # Install Python dependencies
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
  else
    # Try uv first, fall back to pip
    if command -v uv >/dev/null 2>&1; then
      uv sync
    else
      pip install -r requirements.txt
    fi
  fi

  log "INFO" "Dependencies installed successfully."
}

# Setup pre-commit hooks
setup_hooks() {
  local force="$1"

  cd "$PROJECT_ROOT"

  if [[ $force == "true" ]]; then
    log "INFO" "Force reinstalling pre-commit hooks..."
    pre-commit uninstall || true
  fi

  # Check if hooks are already installed
  if pre-commit --version >/dev/null 2>&1; then
    if git config --get core.hooksPath | grep -q ".git/hooks" 2>/dev/null || [[ $force == "true" ]]; then
      log "INFO" "Installing pre-commit hooks..."
      pre-commit install
      log "INFO" "Pre-commit hooks installed successfully!"
    else
      log "INFO" "Pre-commit hooks already installed."
    fi
  else
    log "ERROR" "pre-commit not found. Please install it first."
    exit 1
  fi

  # Initialize secrets baseline if it doesn't exist
  if [[ ! -f ".secrets.baseline" ]]; then
    log "INFO" "Creating secrets baseline file..."
    if command -v detect-secrets >/dev/null 2>&1; then
      detect-secrets scan --baseline .secrets.baseline || true
    else
      log "WARN" "detect-secrets not found. Creating empty baseline."
      echo '{}' >.secrets.baseline
    fi
  fi

  log "INFO" "Running initial hook validation..."
  if pre-commit run --all-files; then
    log "INFO" "✅ All hooks passed initial validation!"
  else
    log "WARN" "⚠️  Some hooks failed. This is normal on first run."
    log "INFO" "Hooks will run automatically on future commits."
  fi
}

# Update hooks
update_hooks() {
  log "INFO" "Updating pre-commit hooks..."

  cd "$PROJECT_ROOT"

  if ! command -v pre-commit >/dev/null 2>&1; then
    log "ERROR" "pre-commit not installed."
    exit 1
  fi

  pre-commit autoupdate
  pre-commit run --all-files || true

  log "INFO" "Hooks updated successfully!"
}

# Uninstall hooks
uninstall_hooks() {
  log "INFO" "Uninstalling pre-commit hooks..."

  cd "$PROJECT_ROOT"

  if command -v pre-commit >/dev/null 2>&1; then
    pre-commit uninstall || true
    log "INFO" "Pre-commit hooks uninstalled."
  else
    log "WARN" "pre-commit not found."
  fi

  # Clean up git hooks directory
  if [[ -d ".git/hooks" ]]; then
    find .git/hooks -name "pre-commit*" -delete || true
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
  install_precommit
  setup_hooks "$force"

  log "INFO" "🎉 Pre-commit setup complete!"
  log "INFO" ""
  log "INFO" "Next steps:"
  log "INFO" "- Hooks will run automatically on every commit"
  log "INFO" "- Run 'pre-commit run --all-files' to check all files"
  log "INFO" "- Run 'pre-commit run <hook-name>' to run specific hooks"
  log "INFO" "- Use 'git commit --no-verify' to skip hooks (not recommended)"
}

# Execute main function with all arguments
main "$@"
