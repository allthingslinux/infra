#!/bin/bash
# uv Setup Script for All Things Linux Infrastructure
# This script sets up the Python environment using uv for dependency management

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if uv is installed
check_uv() {
    if command -v uv &>/dev/null; then
        local uv_version
        uv_version=$(uv --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        log "uv is already installed (version: $uv_version)"
        return 0
    else
        return 1
    fi
}

# Install uv
install_uv() {
    log "Installing uv..."

    # Check if we're on a supported system
    if [[ $OSTYPE == "linux-gnu"* ]] || [[ $OSTYPE == "darwin"* ]]; then
        # Use the official installer
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add uv to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        # Check if installation was successful
        if command -v uv &>/dev/null; then
            success "uv installed successfully!"
        else
            error "uv installation failed. Please add ~/.local/bin to your PATH."
            exit 1
        fi
    else
        error "Unsupported operating system: $OSTYPE"
        echo "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing project dependencies..."

    # Sync all dependencies (production + dev)
    uv sync

    success "Dependencies installed successfully!"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log "Setting up pre-commit hooks..."

    # Install pre-commit hooks using uv's virtual environment
    uv run pre-commit install

    success "Pre-commit hooks installed successfully!"
}

# Generate requirements.txt for compatibility
generate_requirements() {
    log "Generating requirements.txt for compatibility..."

    # Export production dependencies
    uv export --no-dev >requirements.txt

    # Export all dependencies (including dev)
    uv export >requirements-dev.txt

    success "Requirements files generated successfully!"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."

    # Check Python version
    local python_version
    python_version=$(uv run python --version)
    log "Python version: $python_version"

    # Check Ansible version
    if uv run ansible --version &>/dev/null; then
        local ansible_version
        ansible_version=$(uv run ansible --version | head -n1)
        log "Ansible version: $ansible_version"
    else
        warning "Ansible not found in virtual environment"
    fi

    # Check ansible-lint
    if uv run ansible-lint --version &>/dev/null; then
        local lint_version
        lint_version=$(uv run ansible-lint --version)
        log "ansible-lint version: $lint_version"
    else
        warning "ansible-lint not found in virtual environment"
    fi

    success "Installation verification completed!"
}

# Show usage information
show_usage() {
    echo
    echo "=== All Things Linux Infrastructure - uv Setup Complete ==="
    echo
    echo "To activate the virtual environment:"
    echo "  source .venv/bin/activate"
    echo
    echo "To run commands in the virtual environment:"
    echo "  uv run ansible-playbook ..."
    echo "  uv run ansible-lint ..."
    echo "  uv run pytest"
    echo
    echo "To install new dependencies:"
    echo "  uv add <package>                 # Production dependency"
    echo "  uv add --dev <package>           # Development dependency"
    echo
    echo "To update dependencies:"
    echo "  uv sync --upgrade"
    echo
    echo "To run ATL CLI commands:"
    echo "  atl plan                         # Plan infrastructure changes"
    echo "  atl apply                        # Apply infrastructure changes"
    echo "  atl lint                         # Run code quality checks"
    echo
    echo "For more uv commands:"
    echo "  uv --help"
    echo
}

# Main execution
main() {
    echo "=== All Things Linux Infrastructure - uv Setup ==="
    echo

    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        error "pyproject.toml not found. Are you in the project root directory?"
        exit 1
    fi

    # Install uv if not present
    if ! check_uv; then
        install_uv
    fi

    # Install dependencies
    install_dependencies

    # Setup pre-commit hooks
    setup_pre_commit

    # Generate compatibility files
    generate_requirements

    # Verify installation
    verify_installation

    # Show usage information
    show_usage

    success "All Things Linux Infrastructure environment setup completed successfully!"
}

# Run main function
main "$@"
