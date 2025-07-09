# All Things Linux Infrastructure Monorepo

<div align="center">

![All Things Linux](https://img.shields.io/badge/All%20Things-Linux-blue?style=for-the-badge)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Infrastructure as Code](https://img.shields.io/badge/Infrastructure-as%20Code-green?style=for-the-badge)

**Infrastructure-as-Code monorepo for the All Things Linux 501(c)(3) non-profit organization**

[🚀 Quick Start](#-quick-start) • [📁 Structure](#-monorepo-structure) • [🔧 Development](#-development) • [📚 Documentation](docs/)

</div>

## 🏗️ Overview

This **infrastructure monorepo** contains the complete platform-as-code for **All Things Linux**, a 501(c)(3) non-profit organization. We manage infrastructure for 10,000+ community members using modern GitOps practices and infrastructure-as-code principles.

### 🎯 What This Repo Manages

**Infrastructure Only** - Applications live in separate repositories:

- **🏗️ Infrastructure Provisioning** - Terraform for Hetzner Cloud resources
- **⚙️ Configuration Management** - Ansible for server configuration
- **🔍 Monitoring & Observability** - Prometheus, Grafana, and alerting
- **🌐 Network & Security** - Load balancing, SSL, firewalls
- **📦 Platform Services** - Shared services (databases, caching, etc.)

### 📱 Applications (Separate Repos)

Applications deploy **to** this infrastructure but live independently:

- **Discord Bot (Tux)** - Community automation and moderation
- **ATL Wiki** - Educational resources and documentation
- **ATL Tools** - Self-hosted applications suite
- **ATL Chat** - Multi-platform communication bridging
- **ATL Dev** - Developer pubnix and hosting platform

## 🚀 **Quick Start**

### Unified CLI (Recommended)

The `atl` CLI provides a unified interface for all infrastructure operations:

```bash
# Install dependencies
uv sync

# Quick operations
atl plan                    # Plan infrastructure changes
atl apply -y               # Apply changes with auto-approve
atl lint --fix             # Run linting with auto-fix
atl docs build --serve     # Build and serve documentation

# Organized commands
atl infra plan             # Infrastructure planning
atl infra apply            # Infrastructure deployment
atl infra destroy          # Infrastructure destruction
atl quality lint           # Code quality checks
atl docs build             # Documentation generation
atl utils update-collections  # Ansible collections update

# Get help
atl info                   # Show available commands
atl status                 # Check tool availability
atl <command> --help       # Detailed help for any command
```

### Prerequisites

- **Python 3.11+** with uv for dependency management
- **Terraform** for infrastructure provisioning
- **Ansible** for configuration management
- **Hetzner Cloud** account and API token
- **Cloudflare** account and API token

### Installation

1. **Clone and setup:**

   ```bash
   git clone <repository-url>
   cd infra

   # Install dependencies
   uv sync
   uv run ansible-galaxy collection install -r ansible/collections/requirements.yml
   ```

2. **Configure secrets:**

   ```bash
   # Copy secrets template
   cp configs/secrets.example.yml configs/secrets.yml

   # Edit with your actual credentials (never commit this!)
   edit configs/secrets.yml
   ```

3. **Set up development environment:**

   ```bash
   # Install pre-commit hooks
   ./scripts/setup/setup-hooks.sh

   # Run validation
   atl lint
   ```

4. **Deploy infrastructure:**

   ```bash
   # Plan changes first
   cd terraform/environments/staging
   terraform plan

   # Apply infrastructure
   terraform apply

   # Configure servers
   cd ../../../ansible
   ansible-playbook -i inventories/dynamic.py playbooks/site.yml
   ```

## 📁 Monorepo Structure

```
infra/                           # 🏗️ Infrastructure Monorepo
├── 📋 README.md                 # This file
├── 🔧 configs/                  # 🎯 Configuration Management
│   ├── domains.yml              # Domain configurations
│   ├── environments.yml         # Environment definitions
│   └── secrets.example.yml      # Secrets template (never commit secrets.yml!)
│
├── 🏗️ terraform/                # Infrastructure Provisioning
│   ├── modules/                 # Reusable Terraform modules
│   │   ├── network/             # VPC, subnets, security groups
│   │   ├── compute/             # Servers, load balancers
│   │   └── security/            # SSL, firewalls, monitoring
│   ├── environments/            # Environment-specific configs
│   │   ├── production/          # Production infrastructure
│   │   ├── staging/             # Staging environment
│   │   └── development/         # Development environment
│   └── shared/                  # Cross-environment resources (DNS, etc.)
│
├── ⚙️ ansible/                  # Configuration Management
│   ├── ansible.cfg              # Ansible configuration
│   ├── inventories/             # Dynamic and static inventories
│   │   └── dynamic.py           # Dynamic inventory from Terraform
│   ├── playbooks/               # Ansible playbooks
│   │   ├── site.yml             # Main deployment playbook
│   │   ├── infrastructure/      # Infrastructure setup playbooks
│   │   ├── security/            # Security hardening
│   │   └── domains/             # Domain-specific deployments
│   ├── roles/                   # Reusable Ansible roles
│   │   ├── system/              # Base system configuration
│   │   ├── docker/              # Docker and containers
│   │   └── monitoring/          # Monitoring agents
│   ├── group_vars/              # Group variables
│   ├── host_vars/               # Host-specific variables
│   └── collections/             # Ansible collections requirements
│
├── 📊 monitoring/               # Observability Stack
│   ├── prometheus/              # Metrics collection
│   ├── grafana/                 # Dashboards and visualization
│   └── alerting/                # Alert rules and notifications
│
├── 🔧 scripts/                  # Automation and Tooling
│   ├── deploy.py                # Modern Python deployment CLI
│   ├── lint.py                  # Code quality and validation
│   ├── docs.py                  # Documentation generation
│   ├── common/                  # Shared utilities
│   └── setup/                   # Environment setup scripts
│
├── 📚 docs/                     # Infrastructure Documentation
│   ├── guides/                  # How-to guides
│   ├── architecture/            # Architecture decisions
│   ├── runbooks/                # Operational procedures
│   └── setup/                   # Setup and configuration
│
├── 🔄 .github/workflows/        # CI/CD Pipelines
│   ├── terraform.yml            # Infrastructure validation
│   ├── ansible.yml              # Configuration validation
│   └── docs.yml                 # Documentation deployment
│
└── 🐍 Python Environment        # Development Environment
    ├── pyproject.toml            # uv dependencies & CLI tools
├── uv.lock                   # Locked dependencies
    └── mise.toml                 # Development environment
```

### 🏗️ Architecture Principles

This monorepo follows **modern platform engineering** patterns:

- **🔄 GitOps** - Infrastructure changes via git workflows
- **📦 Modular** - Reusable Terraform modules and Ansible roles
- **🌍 Multi-environment** - Consistent dev/staging/production
- **🔍 Observable** - Built-in monitoring and alerting
- **🔒 Secure** - Security hardening and secrets management
- **📱 App-agnostic** - Applications deploy independently

## 🚀 Unified ATL CLI

A single, powerful CLI that consolidates all infrastructure operations into an intuitive interface:

### Unified CLI

The `atl` CLI provides a single interface for all infrastructure operations:

| Command Group | Purpose | Key Features |
|---------------|---------|-------------|
| `atl infra` | Infrastructure management | Terraform + Ansible deployment with rich output |
| `atl quality` | Code quality validation | Multi-format linting, auto-fix capabilities |
| `atl docs` | Documentation generation | Automated docs from infrastructure code |
| `atl utils` | Utility operations | Collection updates, maintenance tasks |

### Usage Examples

```bash
# Quick access commands
atl plan                            # Preview infrastructure changes
atl apply                           # Apply infrastructure changes
atl lint                            # Run validation checks

# Organized commands
atl infra plan --environment staging
atl infra apply --environment production
atl quality lint --fix             # Auto-fix common issues
atl docs build --serve             # Generate and serve documentation

# Get help and status
atl info                            # Show all available commands
atl status                          # Check tool availability
```

## 🎭 Role-Based Access Control

Comprehensive team access management:

### Infrastructure Teams

- **🔧 Platform Engineering**: Full infrastructure access
- **☁️ Cloud Operations**: Environment management and monitoring
- **🔒 Security**: Security policies and compliance
- **📊 Site Reliability**: Monitoring and incident response

### Development Teams

- **🖥️ Backend Engineers**: API and service deployment
- **🎨 Frontend Engineers**: Web application deployment
- **🐍 Python Developers**: Discord bot and tools deployment
- **📱 Mobile Developers**: Mobile app infrastructure

### Community Teams

- **👨‍💼 Management**: Oversight and resource allocation
- **🛡️ Moderation**: Community management tools
- **🎨 Creative**: Content and brand management

## 🏗️ Infrastructure Overview

### Multi-Environment Strategy

| Environment | Purpose | Infrastructure |
|-------------|---------|---------------|
| **Production** | Live services | High-availability, monitoring, backups |
| **Staging** | Pre-production testing | Production-like, automated testing |
| **Development** | Feature development | Lightweight, rapid iteration |

### Core Platform Services

- **🌐 Load Balancing**: HAProxy with automatic failover
- **🗄️ Databases**: PostgreSQL clusters with Redis caching
- **📊 Monitoring**: Prometheus + Grafana + AlertManager
- **🔍 Logging**: Centralized log aggregation and analysis
- **🔒 Security**: Automated security scanning and hardening
- **💾 Backups**: Automated backup and disaster recovery

## 🔧 Development

### Local Development Setup

```bash
# Install development dependencies
uv sync

# Set up pre-commit hooks
./scripts/setup/setup-hooks.sh

# Validate your setup
atl lint
```

### Workflow

1. **🌿 Branch**: Create feature branch from `main`
2. **💻 Develop**: Make infrastructure changes
3. **✅ Validate**: Run `atl lint`
4. **🧪 Test**: Deploy to development environment
5. **📝 Document**: Update relevant documentation
6. **🔄 PR**: Create pull request for review
7. **🚀 Deploy**: Merge triggers deployment pipeline

### Testing

```bash
# Syntax validation
atl lint

# Infrastructure planning
cd terraform/environments/development
terraform plan

# Configuration testing
cd ansible
ansible-playbook --syntax-check playbooks/site.yml
```

## 📚 Documentation

Comprehensive documentation available in [`docs/`](docs/):

- **[📋 Setup Guide](docs/setup/)** - Installation and configuration
- **[🏗️ Architecture](docs/architecture/)** - System design and decisions
- **[📖 Runbooks](docs/runbooks/)** - Operational procedures
- **[🔧 Development](docs/guides/development.md)** - Development workflow

## 🤝 Contributing

1. **📖 Read** the [development guide](docs/guides/development.md)
2. **🍴 Fork** this repository
3. **🌿 Create** a feature branch
4. **✅ Test** your changes thoroughly
5. **📝 Document** any new features
6. **🔄 Submit** a pull request

## 📄 License

This infrastructure code is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**[All Things Linux](https://allthingslinux.org)** • A 501(c)(3) Non-Profit Organization

*Empowering the Linux ecosystem through education, collaboration, and open infrastructure*

</div>

### Development Environment

For local development and testing of Ansible roles, please refer to the [Local Development Environment Guide](./docs/guides/development-environment.md).

### Production Deployment

> **Warning:** The following commands will provision and modify live production infrastructure.

1. **Initialize Terraform:**

    ```sh
    cd terraform/environments/production
    terraform init
    ```

2. **Apply Terraform Plan:**

    ```sh
    terraform apply
    ```

3. **Run Ansible Playbook:**
    Once infrastructure is provisioned, apply the configuration with Ansible:

    ```sh
    ansible-playbook -i inventories/production site.yml
    ```

## 🤝 Contributing

Please see `CONTRIBUTING.md` for details on how to contribute to this project.
