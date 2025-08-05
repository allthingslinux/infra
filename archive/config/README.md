# Configuration Files

This directory contains all configuration files organized by category.

## Directory Structure

```
config/
├── ansible/                    # Ansible configuration files
│   ├── ansible.cfg            # Ansible main configuration
│   └── .ansible-lint          # Ansible linting rules
├── terraform/                  # Terraform configuration files
│   └── .tflint.hcl           # Terraform linting rules
├── security/                   # Security scanning configuration
│   ├── .gitleaks.toml        # GitLeaks configuration
│   └── .trivyignore          # Trivy ignore rules
├── linting/                    # General linting configuration
│   └── .yamllint.yml         # YAML linting rules
├── domains.yml                # Domain definitions (SINGLE SOURCE for server specs)
├── environments.yml           # Environment configurations (NO server specs)
├── secrets.example.yml        # Secret templates
└── README.md                 # This file
```

## Configuration Categories

### Application Configs (Single Source of Truth)

- **domains.yml**: Domain definitions and server specifications (SINGLE SOURCE)
- **environments.yml**: Environment-specific configurations (NO server specs)
- **secrets.example.yml**: Secret templates and examples

### Tool Configs (Tool-Specific)

- **ansible/**: Ansible configuration and linting
- **terraform/**: Terraform linting and validation
- **security/**: Security scanning configurations
- **linting/**: General linting rules

## Single Source of Truth

### Server Specifications

**ALL server types, locations, and specifications are defined in `domains.yml`**:

```yaml
# config/domains.yml - SINGLE SOURCE
domains:
  atl_services:
    server:
      type: "cx31"      # Domain-specific server type
      location: "ash"    # Domain-specific location
      count: 1
  atl_tools:
    server:
      type: "cx31"      # Different domain, same server type
      location: "ash"
      count: 1
  atl_chat:
    server:
      type: "cx21"      # Different domain, different server type
      location: "ash"
      count: 1
```

This is referenced by:

- Terraform environments (should read from domains.yml)
- Ansible group_vars (should read from domains.yml)
- Dynamic inventory (should read from domains.yml)

### Environment Configurations

Environment-specific settings are in `environments.yml` (NO server specs):

```yaml
# config/environments.yml - NO server specs
environments:
  production:
    network_range: "10.0.0.0/16"
    location: "ash"
    # NO server_type here - comes from domains.yml
```

## Usage

### Ansible Configuration

```bash
# Use custom ansible.cfg
export ANSIBLE_CONFIG=config/ansible/ansible.cfg
ansible-playbook playbook.yml
```

### Terraform Linting

```bash
# Use custom tflint config
tflint --config config/terraform/.tflint.hcl
```

### Security Scanning

```bash
# Use custom gitleaks config
gitleaks detect --config config/security/.gitleaks.toml
```

## Notes

- **Single source of truth**: Server specs ONLY in domains.yml
- **No duplication**: No server specs in environments.yml or Terraform files
- **Tool isolation**: Each tool's config is in its own subdirectory
- **Clear separation**: Application configs vs tool configs
- **Domain-driven**: Each domain defines its own server requirements
