# Infrastructure Development Guide

This guide covers development workflows, best practices, and contribution guidelines for the All Things Linux infrastructure monorepo.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with uv
- **Terraform** >= 1.6
- **Git** with SSH keys configured
- **Docker** (for local testing)
- **Hetzner Cloud** and **Cloudflare** accounts

### Initial Setup

```bash
# Clone the repository
git clone git@github.com:allthingslinux/infra.git
cd infra

# Install dependencies
uv sync

# Install Ansible collections
uv run ansible-galaxy collection install -r ansible/collections/requirements.yml

# Set up lefthook hooks
./scripts/setup/setup-hooks.sh

# Validate your setup
atl lint
```

### Environment Configuration

1. **Copy secrets template:**

   ```bash
   cp configs/secrets.example.yml configs/secrets.yml
   ```

2. **Edit secrets with your credentials:**

   ```bash
   # Edit configs/secrets.yml with your actual API tokens
   # Never commit this file - it's in .gitignore
   ```

3. **Configure Terraform environment:**

   ```bash
   cd terraform/environments/development
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your Hetzner token
   ```

## 🏗️ Repository Structure

### Key Directories

- **`terraform/`** - Infrastructure provisioning
  - `modules/` - Reusable Terraform modules
  - `environments/` - Environment-specific configurations
- **`ansible/`** - Configuration management
  - `playbooks/` - Ansible playbooks
  - `roles/` - Reusable Ansible roles
  - `inventories/` - Dynamic and static inventories
- **`configs/`** - Shared configuration files
- **`monitoring/`** - Observability stack configurations
- **`scripts/`** - Automation and utility scripts
- **`docs/`** - Documentation

### Configuration Hierarchy

```
configs/
├── environments.yml    # Environment definitions
├── domains.yml        # Domain configurations
└── secrets.yml        # Sensitive credentials (never commit!)

terraform/environments/{environment}/
├── main.tf            # Environment-specific infrastructure
├── variables.tf       # Environment variables
├── outputs.tf         # Environment outputs
└── terraform.tfvars   # Environment configuration (never commit!)
```

## 🔧 Development Workflow

### 1. Branch Strategy

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Or for infrastructure changes
git checkout -b infra/add-monitoring-stack
```

### 2. Making Changes

#### Infrastructure Changes (Terraform)

```bash
# Navigate to environment
cd terraform/environments/development

# Plan changes
terraform plan

# Apply changes (after review)
terraform apply

# Validate in development first!
```

#### Configuration Changes (Ansible)

```bash
# Validate syntax
cd ansible
ansible-playbook --syntax-check playbooks/site.yml

# Run against development
ansible-playbook -i inventories/development.yml playbooks/site.yml --check

# Apply changes
ansible-playbook -i inventories/development.yml playbooks/site.yml
```

### 3. Quality Checks

```bash
# Run all linting
atl lint

# Fix auto-fixable issues
atl lint --fix

# Run specific checks
atl quality lint --target terraform
atl quality lint --target ansible
```

### 4. Testing

```bash
# Test in development environment
cd terraform/environments/development
terraform plan

# Deploy to development
terraform apply

# Validate with Ansible
cd ../../../ansible
ansible-playbook -i inventories/development.yml playbooks/site.yml --check
```

### 5. Documentation

```bash
# Generate documentation
atl docs build

# Build documentation site
mkdocs build

# Serve documentation locally
mkdocs serve
```

### 6. Commit and Push

```bash
# Stage changes
git add .

# Commit with conventional commit format
git commit -m "feat(terraform): add monitoring module"
git commit -m "fix(ansible): correct firewall rules"
git commit -m "docs: update development guide"

# Push and create PR
git push origin feature/your-feature-name
```

## 📋 Development Standards

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/), automatically validated by [commitlint](https://pypi.org/project/commitlint/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Scopes:**

- `terraform`: Infrastructure changes
- `ansible`: Configuration management
- `monitoring`: Observability changes
- `docs`: Documentation
- `scripts`: Automation tools

### Code Style

#### Terraform

```hcl
# Use descriptive resource names
resource "hcloud_server" "web_server" {
  name = "${var.environment}-web-${count.index + 1}"
  # ...
}

# Always include descriptions for variables
variable "server_count" {
  description = "Number of web servers to create"
  type        = number
  default     = 2
}

# Use locals for complex expressions
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = "atl"
  }
}
```

#### Ansible

```yaml
# Use descriptive task names
- name: Install and configure nginx
  package:
    name: nginx
    state: present
  become: true

# Always use fully qualified collection names
- name: Create firewall rule
  community.general.ufw:
    rule: allow
    port: 80

# Use variables for reusability
- name: Configure application
  template:
    src: app.conf.j2
    dest: "/etc/app/{{ app_name }}.conf"
  vars:
    app_port: "{{ app_config.port }}"
```

### Security Best Practices

1. **Never commit secrets** - Use `configs/secrets.yml` (gitignored)
2. **Use least privilege** - Minimal required permissions
3. **Enable encryption** - All data at rest and in transit
4. **Regular updates** - Keep dependencies updated
5. **Audit access** - Log and monitor all access

### Infrastructure Design Principles

1. **Immutable Infrastructure** - Replace, don't modify
2. **Infrastructure as Code** - Everything in version control
3. **Environment Parity** - Dev/staging/prod consistency
4. **Observability First** - Built-in monitoring and logging
5. **Security by Default** - Secure configurations by default

## 🧪 Testing Strategy

### Local Testing

```bash
# Terraform validation
terraform fmt -check -recursive terraform/
terraform validate

# Ansible validation
ansible-lint ansible/
ansible-playbook --syntax-check ansible/playbooks/site.yml

# YAML validation
yamllint configs/ ansible/
```

### Development Environment

```bash
# Deploy to development
cd terraform/environments/development
terraform apply

# Configure with Ansible
cd ../../../ansible
ansible-playbook -i inventories/development.yml playbooks/site.yml

# Verify deployment
ansible all -i inventories/development.yml -m ping
```

### Integration Testing

```bash
# Test connectivity
ansible all -i inventories/development.yml -m setup

# Test services
ansible web -i inventories/development.yml -m uri -a "url=http://localhost"

# Test monitoring
curl http://prometheus.dev.allthingslinux.org/-/healthy
```

## 🔍 Debugging

### Terraform Issues

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan

# Inspect state
terraform show
terraform state list

# Import existing resources
terraform import hcloud_server.example 12345
```

### Ansible Issues

```bash
# Increase verbosity
ansible-playbook -vvv playbooks/site.yml

# Check facts
ansible hostname -m setup

# Test connectivity
ansible all -m ping

# Run specific tasks
ansible-playbook playbooks/site.yml --tags "firewall"
```

### Infrastructure Debugging

```bash
# Check server status
cd terraform/environments/development
terraform output server_info

# SSH to server
ssh -i ~/.ssh/id_rsa root@SERVER_IP

# Check logs
journalctl -f
docker logs container_name
```

## 📊 Monitoring Development

### Local Monitoring Stack

```bash
# Start monitoring stack
cd monitoring
docker-compose up -d

# Access interfaces
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
open http://localhost:9093  # Alertmanager
```

### Metrics Collection

```bash
# Check metrics endpoints
curl http://localhost:9100/metrics  # Node exporter
curl http://localhost:9090/metrics  # Prometheus

# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'
```

## 🚀 Deployment Process

### Development → Staging

1. **Test in Development**

   ```bash
   # Validate changes
   cd terraform/environments/development
   terraform plan && terraform apply
   ```

2. **Update Staging**

   ```bash
   # Deploy to staging
   cd ../staging
   terraform plan && terraform apply
   ```

3. **Validate Staging**

   ```bash
   # Run integration tests
   ansible-playbook -i inventories/staging.yml playbooks/verification.yml
   ```

### Staging → Production

1. **Final Review** - All changes peer-reviewed
2. **Maintenance Window** - Schedule if needed
3. **Deploy Production**

   ```bash
   cd terraform/environments/production
   terraform plan && terraform apply
   ```

4. **Verify** - Full system validation
5. **Monitor** - Watch metrics and alerts

## 🤝 Contributing

### Pull Request Process

1. **Fork and Branch** - Create feature branch
2. **Develop** - Make your changes
3. **Test** - Validate in development environment
4. **Document** - Update relevant documentation
5. **Submit PR** - Use PR template
6. **Review** - Address feedback
7. **Merge** - Squash and merge

### PR Requirements

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Breaking changes documented
- [ ] Tested in development environment

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Security best practices followed
- [ ] Infrastructure changes are reversible
- [ ] Documentation is comprehensive
- [ ] Tests validate functionality

## 📚 Resources

### Documentation

- [Architecture Overview](../architecture/overview.md)
- [Deployment Guide](deployment.md)
- [Troubleshooting](../reference/troubleshooting.md)
- [Commands Reference](../reference/commands.md)

### External Resources

- [Terraform Documentation](https://terraform.io/docs)
- [Ansible Documentation](https://docs.ansible.com)
- [Hetzner Cloud API](https://docs.hetzner.cloud)
- [Cloudflare API](https://developers.cloudflare.com/api)

### Community

- **Discord**: ATL Development channels
- **GitHub Issues**: Bug reports and feature requests
- **Wiki**: Community documentation

---

*This guide is living documentation. Please update it as the infrastructure evolves.*
