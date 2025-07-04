#!/bin/bash
# Poetry Setup Script for All Things Linux Infrastructure
# This script sets up the Python environment using Poetry for dependency management

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

# Check if Poetry is installed
check_poetry() {
    if command -v poetry &>/dev/null; then
        local poetry_version=$(poetry --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        log "Poetry is already installed (version: $poetry_version)"
        return 0
    else
        return 1
    fi
}

# Install Poetry
install_poetry() {
    log "Installing Poetry..."

    # Check if we're on a supported system
    if [[ $OSTYPE == "linux-gnu"* ]] || [[ $OSTYPE == "darwin"* ]]; then
        # Use the official installer
        curl -sSL https://install.python-poetry.org | python3 -

        # Add Poetry to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        # Check if installation was successful
        if command -v poetry &>/dev/null; then
            success "Poetry installed successfully!"
        else
            error "Poetry installation failed. Please add ~/.local/bin to your PATH."
            echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
            echo 'export PATH="$HOME/.local/bin:$PATH"'
            exit 1
        fi
    else
        error "Unsupported operating system: $OSTYPE"
        echo "Please install Poetry manually: https://python-poetry.org/docs/#installation"
        exit 1
    fi
}

# Configure Poetry
configure_poetry() {
    log "Configuring Poetry..."

    # Configure Poetry to create virtual environments in project directory
    poetry config virtualenvs.in-project true

    # Configure Poetry to use system certificates (useful in corporate environments)
    poetry config certificates.system-ca-store true

    success "Poetry configured successfully!"
}

# Install dependencies
install_dependencies() {
    log "Installing project dependencies..."

    # Install all dependencies (production + dev)
    poetry install

    success "Dependencies installed successfully!"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log "Setting up pre-commit hooks..."

    # Install pre-commit hooks using Poetry's virtual environment
    poetry run pre-commit install

    success "Pre-commit hooks installed successfully!"
}

# Generate requirements.txt for compatibility
generate_requirements() {
    log "Generating requirements.txt for compatibility..."

    # Export production dependencies
    poetry export -f requirements.txt --output requirements.txt --without-hashes

    # Export dev dependencies
    poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

    success "Requirements files generated successfully!"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."

    # Check Python version
    local python_version=$(poetry run python --version)
    log "Python version: $python_version"

    # Check Ansible version
    if poetry run ansible --version &>/dev/null; then
        local ansible_version=$(poetry run ansible --version | head -n1)
        log "Ansible version: $ansible_version"
    else
        warning "Ansible not found in virtual environment"
    fi

    # Check ansible-lint
    if poetry run ansible-lint --version &>/dev/null; then
        local lint_version=$(poetry run ansible-lint --version)
        log "ansible-lint version: $lint_version"
    else
        warning "ansible-lint not found in virtual environment"
    fi

    success "Installation verification completed!"
}

# Show usage information
show_usage() {
    echo
    echo "=== All Things Linux Infrastructure - Poetry Setup Complete ==="
    echo
    echo "To activate the virtual environment:"
    echo "  poetry shell"
    echo
    echo "To run commands in the virtual environment:"
    echo "  poetry run ansible-playbook ..."
    echo "  poetry run ansible-lint ..."
    echo "  poetry run pytest"
    echo
    echo "To install new dependencies:"
    echo "  poetry add <package>              # Production dependency"
    echo "  poetry add --group dev <package>  # Development dependency"
    echo
    echo "To update dependencies:"
    echo "  poetry update"
    echo
    echo "To run ATL CLI commands:"
    echo "  atl plan                         # Plan infrastructure changes"
    echo "  atl apply                        # Apply infrastructure changes"
    echo "  atl lint                         # Run code quality checks"
    echo
    echo "For more Poetry commands:"
    echo "  poetry --help"
    echo
}

# Main execution
main() {
    echo "=== All Things Linux Infrastructure - Poetry Setup ==="
    echo

    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        error "pyproject.toml not found. Are you in the project root directory?"
        exit 1
    fi

    # Install Poetry if not present
    if ! check_poetry; then
        install_poetry
    fi

    # Configure Poetry
    configure_poetry

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

    success "Poetry setup completed successfully!"
}

# Run main function
main "$@"
