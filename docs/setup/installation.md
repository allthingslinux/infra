# Installation Guide

This guide will help you install all dependencies and tools needed for the All Things Linux infrastructure.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.10 or higher
- **Git**: Latest version
- **SSH**: Client configured

### Hardware Requirements

- **Development**: 4GB RAM, 20GB disk space
- **Staging/Production**: Access to Hetzner Cloud and Cloudflare accounts

## 🐍 Python Environment Setup

### Install uv (Recommended)

uv provides fast dependency management, virtual environments, and reproducible builds:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to your shell profile)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
uv --version
```

### Alternative: pip + venv

If you prefer traditional Python tools:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip
```

## 📦 Install Dependencies

### Method 1: uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/allthingslinux/infra.git
cd infra

# Install all dependencies
uv sync

# Activate the environment
source .venv/bin/activate
```

### Method 2: pip Requirements

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r ansible/collections/requirements.yml
```

## 🔧 Tool Installation

### Ansible Collections

```bash
# Install required Ansible collections
ansible-galaxy collection install -r ansible/collections/requirements.yml

# Verify installation
ansible-galaxy collection list
```

### Development Tools

uv automatically installs these, but for manual setup:

```bash
# Code quality tools
pip install ansible-lint yamllint pre-commit

# Testing tools
pip install molecule pytest

# Docker support
# Note: Docker Compose v2 is included with Docker Desktop
# For Linux: Follow Docker installation guide
```

### External Tools

#### Docker & Docker Compose

**Ubuntu/Debian:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

**macOS:**

```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://docker.com/products/docker-desktop
```

#### Terraform (Optional)

Only needed for direct Terraform operations:

```bash
# Install via package manager
# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# macOS
brew install terraform

# Verify installation
terraform --version
```

## 🪝 Development Environment Setup

### Pre-commit Hooks

Set up automated code quality checks:

```bash
# Install pre-commit hooks
./scripts/setup-hooks.sh

# Or manually:
pre-commit install
pre-commit install --hook-type commit-msg

# Test hooks
pre-commit run --all-files
```

### IDE Configuration

#### VS Code Extensions

Recommended extensions for VS Code:

```json
{
  "recommendations": [
    "redhat.ansible",
    "redhat.vscode-yaml",
    "ms-python.python",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "hashicorp.terraform"
  ]
}
```

#### Vim/Neovim

Install language servers:

```bash
# Python
pip install python-lsp-server

# Ansible
ansible-galaxy collection install ansible.posix
pip install ansible-language-server

# Terraform
# Install terraform-ls from: https://github.com/hashicorp/terraform-ls
```

## ✅ Verify Installation

### Check Python Environment

```bash
# Verify Python version
python --version  # Should be 3.10+

# Check uv environment
uv run python --version

# List installed packages
uv pip list
```

### Check Ansible

```bash
# Verify Ansible installation
ansible --version
ansible-galaxy --version

# Test Ansible configuration
ansible-config dump

# List installed collections
ansible-galaxy collection list
```

### Check Tools

```bash
# Development tools
ansible-lint --version
yamllint --version
pre-commit --version

# Docker
docker --version
docker compose version

# Terraform (if installed)
terraform --version
```

### Test Project Setup

```bash
# Test linting
atl lint

# Test configuration display
atl config

# Run a dry-run deployment (requires configuration)
# atl apply --dry-run --target domain --domain-name example
```

## 🐧 Platform-Specific Notes

### Linux

Most tools install via package managers:

```bash
# Ubuntu/Debian additional packages
sudo apt update
sudo apt install -y python3-pip python3-venv git openssh-client

# Fedora/RHEL
sudo dnf install -y python3-pip python3-virtualenv git openssh-clients

# Arch Linux
sudo pacman -S python-pip git openssh
```

### macOS

Use Homebrew for easy installation:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install python git openssh
```

### Windows (WSL2)

Use Windows Subsystem for Linux:

```bash
# Install WSL2 and Ubuntu
wsl --install

# Then follow Linux instructions above
```

## 🚨 Troubleshooting

### Common Issues

#### uv not found

```bash
# Add uv to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Python version conflicts

```bash
# Use specific Python version with uv
uv python install 3.10
uv python pin 3.10

# Or with pyenv
pyenv install 3.10.12
pyenv local 3.10.12
```

#### Permission errors

```bash
# Fix pip permissions (avoid sudo with pip)
python -m pip install --user --upgrade pip

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### Ansible collections fail

```bash
# Clear cache and retry
ansible-galaxy collection install -r ansible/collections/requirements.yml --force

# Manual installation
ansible-galaxy collection install community.general community.docker
```

## 📝 Next Steps

After successful installation:

1. **[Configuration Guide](configuration.md)** - Set up environment variables and SSH keys
2. **[Deployment Guide](../guides/deployment.md)** - Deploy your first environment
3. **[Development Workflow](../guides/development.md)** - Learn the development process

## 📚 Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Pre-commit Documentation](https://pre-commit.com/)
