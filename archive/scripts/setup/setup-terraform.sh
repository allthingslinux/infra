#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TERRAFORM_VERSION="1.6.6"
INSTALL_DIR="/usr/local/bin"
FORCE_INSTALL=false

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Install Terraform for infrastructure management

Options:
    -v, --version VERSION    Terraform version to install [default: $TERRAFORM_VERSION]
    -d, --install-dir DIR    Installation directory [default: $INSTALL_DIR]
    -f, --force             Force reinstallation if already exists
    -h, --help              Show this help message

Examples:
    $0                      # Install latest stable version
    $0 -v 1.6.6            # Install specific version
    $0 -f                   # Force reinstall

EOF
}

log() {
  echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}"
}

error() {
  echo -e "${RED}[ERROR] $*${NC}" >&2
}

warn() {
  echo -e "${YELLOW}[WARNING] $*${NC}"
}

success() {
  echo -e "${GREEN}[SUCCESS] $*${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  -v | --version)
    TERRAFORM_VERSION="$2"
    shift 2
    ;;
  -d | --install-dir)
    INSTALL_DIR="$2"
    shift 2
    ;;
  -f | --force)
    FORCE_INSTALL=true
    shift
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    error "Unknown option: $1"
    usage
    exit 1
    ;;
  esac
done

# Detect architecture and OS
detect_platform() {
  local arch
  local os

  case "$(uname -m)" in
  x86_64)
    arch="amd64"
    ;;
  arm64 | aarch64)
    arch="arm64"
    ;;
  *)
    error "Unsupported architecture: $(uname -m)"
    exit 1
    ;;
  esac

  case "$(uname -s)" in
  Linux)
    os="linux"
    ;;
  Darwin)
    os="darwin"
    ;;
  *)
    error "Unsupported operating system: $(uname -s)"
    exit 1
    ;;
  esac

  echo "${os}_${arch}"
}

# Check if Terraform is already installed
check_existing() {
  if command -v terraform &>/dev/null; then
    local current_version
    current_version=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

    if [[ $current_version == "$TERRAFORM_VERSION" ]] && [[ $FORCE_INSTALL != "true" ]]; then
      success "Terraform $current_version is already installed"
      terraform version
      exit 0
    else
      warn "Terraform $current_version is installed, but version $TERRAFORM_VERSION was requested"
      if [[ $FORCE_INSTALL != "true" ]]; then
        warn "Use --force to reinstall"
        exit 1
      fi
    fi
  fi
}

# Download and install Terraform
install_terraform() {
  local platform
  platform=$(detect_platform)

  local download_url="https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${platform}.zip"
  local temp_dir
  temp_dir=$(mktemp -d)

  log "Downloading Terraform $TERRAFORM_VERSION for $platform..."

  # Download Terraform
  if ! curl -fsSL "$download_url" -o "$temp_dir/terraform.zip"; then
    error "Failed to download Terraform from $download_url"
    rm -rf "$temp_dir"
    exit 1
  fi

  # Extract Terraform
  log "Extracting Terraform..."
  if ! unzip -q "$temp_dir/terraform.zip" -d "$temp_dir"; then
    error "Failed to extract Terraform"
    rm -rf "$temp_dir"
    exit 1
  fi

  # Install Terraform
  log "Installing Terraform to $INSTALL_DIR..."

  # Check if we need sudo
  if [[ ! -w $INSTALL_DIR ]]; then
    log "Installing with sudo (directory not writable)..."
    sudo mv "$temp_dir/terraform" "$INSTALL_DIR/terraform"
    sudo chmod +x "$INSTALL_DIR/terraform"
  else
    mv "$temp_dir/terraform" "$INSTALL_DIR/terraform"
    chmod +x "$INSTALL_DIR/terraform"
  fi

  # Cleanup
  rm -rf "$temp_dir"

  # Verify installation
  if command -v terraform &>/dev/null; then
    success "Terraform installed successfully!"
    terraform version
  else
    error "Terraform installation failed - binary not found in PATH"
    error "Make sure $INSTALL_DIR is in your PATH"
    exit 1
  fi
}

# Setup Terraform completion
setup_completion() {
  log "Setting up Terraform shell completion..."

  # For bash
  if [[ -n ${BASH_VERSION:-} ]]; then
    local bash_completion_dir
    if [[ -d "/etc/bash_completion.d" ]]; then
      bash_completion_dir="/etc/bash_completion.d"
    elif [[ -d "/usr/local/etc/bash_completion.d" ]]; then
      bash_completion_dir="/usr/local/etc/bash_completion.d"
    else
      bash_completion_dir="$HOME/.bash_completion.d"
      mkdir -p "$bash_completion_dir"
    fi

    if terraform -install-autocomplete 2>/dev/null || terraform completion bash >"$bash_completion_dir/terraform" 2>/dev/null; then
      success "Bash completion installed"
    else
      warn "Could not install bash completion"
    fi
  fi

  # For zsh
  if [[ -n ${ZSH_VERSION:-} ]]; then
    if terraform -install-autocomplete 2>/dev/null; then
      success "Zsh completion installed"
    else
      warn "Could not install zsh completion"
    fi
  fi
}

# Verify dependencies
check_dependencies() {
  local missing_deps=()

  # Check for required tools
  if ! command -v curl &>/dev/null; then
    missing_deps+=("curl")
  fi

  if ! command -v unzip &>/dev/null; then
    missing_deps+=("unzip")
  fi

  if ! command -v jq &>/dev/null; then
    warn "jq not found - some features may not work properly"
  fi

  if [[ ${#missing_deps[@]} -gt 0 ]]; then
    error "Missing required dependencies: ${missing_deps[*]}"
    error "Please install them and try again"
    exit 1
  fi
}

# Main execution
main() {
  log "Setting up Terraform $TERRAFORM_VERSION"

  check_dependencies
  check_existing
  install_terraform
  setup_completion

  success "Terraform setup complete!"
  log "You can now use: ./scripts/terraform-deploy.sh"
  log "See docs/TERRAFORM_HETZNER_GUIDE.md for usage instructions"
}

# Run main function
main
