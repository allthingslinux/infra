# ATL CLI Commands Reference

Complete reference for the unified `atl` CLI tool.

## 🎯 **Getting Started**

```bash
# Get oriented with the CLI
atl info                    # Show all available commands
atl status                  # Check tool availability
atl --help                  # Main help
```

## 🏗️ **Infrastructure Commands (`atl infra`)**

### Basic Infrastructure Operations

```bash
# Plan infrastructure changes
atl infra plan

# Apply infrastructure changes
atl infra apply

# Show current configuration
atl infra config

# Destroy infrastructure (use with caution!)
atl infra destroy --auto-approve
```

### Environment-Specific Operations

```bash
# Plan for specific environment
atl infra plan --environment staging
atl infra apply --environment production
```

### Target-Specific Deployments

```bash
# Deploy everything
atl infra apply --target all

# Deploy only infrastructure (Terraform)
atl infra apply --target infrastructure

# Deploy only domains
atl infra apply --target domains

# Deploy specific domain
atl infra apply --target domain --domain-name myapp.allthingslinux.dev
```

### Advanced Options

```bash
# Dry run (show what would be deployed)
atl infra apply --dry-run

# Verbose output
atl infra apply --verbose

# Auto-approve changes
atl infra apply --auto-approve

# Ansible only (skip Terraform)
atl infra apply --ansible-only

# Terraform only (skip Ansible)
atl infra apply --terraform-only
```

### Domain Management

```bash
# Enable a domain
atl infra enable myapp.allthingslinux.dev

# Disable a domain
atl infra disable old.allthingslinux.dev

# Show configuration
atl infra config
```

### Infrastructure Validation

```bash
# Run syntax check
atl infra check

# Combined linting (also available)
atl infra lint
```

## ✅ **Quality Commands (`atl quality`)**

### Basic Linting

```bash
# Run all linting checks
atl quality lint

# Fix auto-fixable issues
atl quality lint --fix

# Verbose output
atl quality lint --verbose

# Strict mode (exit on warnings)
atl quality lint --strict
```

### Target-Specific Linting

```bash
# Lint everything
atl quality lint --target all

# Lint only playbooks
atl quality lint --target playbooks

# Lint only inventories
atl quality lint --target inventories

# Lint only roles
atl quality lint --target roles
```

### Output Formats

```bash
# Default output
atl quality lint

# JSON output
atl quality lint --format json

# Code Climate format
atl quality lint --format codeclimate

# SARIF format (for GitHub)
atl quality lint --format sarif
```

## 📚 **Documentation Commands (`atl docs`)**

### Build Documentation

```bash
# Build documentation
atl docs build

# Build and serve locally
atl docs build --serve

# Serve on specific port/host
atl docs build --serve --port 8080 --host 0.0.0.0

# Open browser automatically
atl docs build --serve --open-browser
```

### Generate Diagrams

```bash
# Generate infrastructure diagrams
atl docs diagrams

# Specify output directory
atl docs diagrams --output-dir assets/diagrams

# Specify format
atl docs diagrams --format png
atl docs diagrams --format pdf
atl docs diagrams --format svg
```

## 🔧 **Utility Commands (`atl utils`)**

### Ansible Collections

```bash
# Update Ansible collections
atl utils update-collections

# Force update (even if up to date)
atl utils update-collections --force

# Verbose output
atl utils update-collections --verbose
```

### Log Management

The ATL CLI automatically manages log files to prevent clutter:

#### Automatic Cleanup

- **Runs automatically**: Each time you use ATL tools, old logs are cleaned up
- **Per-tool limits**: Keeps only the 5 most recent log files per tool type
- **Time-based**: Removes logs older than 7 days
- **Safe operation**: Never removes logs that might be in use

#### Manual Cleanup

```bash
# Clean up with default settings (5 files per tool, 7 days max age)
atl utils cleanup-logs

# Custom retention (keep 10 files per tool, 14 days max age)
atl utils cleanup-logs --max-files 10 --max-age 14

# Preview what would be cleaned
atl utils cleanup-logs --dry-run
```

#### Log Organization

Log files are organized by tool type with timestamps:

```text
logs/
├── deploy-20240704_052731.log    # Most recent deploy log
├── docs-20240704_052420.log      # Most recent docs log
├── lint-20240703_222915.log      # Most recent lint log
└── ...                           # Additional recent logs
```

## ⚡ **Quick Access Commands**

For frequently used operations, quick access commands are available at the top level:

```bash
# Infrastructure operations
atl plan                    # Same as: atl infra plan
atl apply                   # Same as: atl infra apply

# Quality operations
atl lint                    # Same as: atl quality lint
```

### Quick Access with Options

```bash
# Plan with environment
atl plan --environment production

# Apply with auto-approve
atl apply --auto-approve

# Lint with fix
atl lint --fix
```

## 🔍 **Global Options**

Most commands support these global options:

- `--environment, -e`: Target environment (development/staging/production)
- `--verbose, -v`: Enable verbose output
- `--dry-run, -d`: Show what would be changed without making changes
- `--help`: Show detailed help for any command

## 🔐 **Secrets and Authentication**

### Environment Variables for Terraform

```bash
# Set Hetzner Cloud token for Terraform
export TF_VAR_hetzner_token="your-hetzner-token"

# Set Cloudflare token for Terraform
export TF_VAR_cloudflare_token="your-cloudflare-token"

# Apply with environment variables
atl infra apply --ask-vault-pass
```

### Configuration Validation

```bash
# Show current configuration (masks secrets)
atl infra config

# Run configuration validation
atl infra check
```

## 🧪 **Testing and Debugging**

### Dry Run Operations

```bash
# Test infrastructure changes without applying
atl infra apply --dry-run --target domain --domain-name example
```

### Debugging

```bash
# Enable verbose output for debugging
atl infra apply --verbose
atl quality lint --verbose
```

## 🆘 **Help System**

### Command Help

```bash
# Main help
atl --help

# Group-specific help
atl infra --help
atl quality --help
atl docs --help
atl utils --help

# Command-specific help
atl infra plan --help
atl quality lint --help
```

### Discovery

```bash
# Show organized overview of all commands
atl info

# Check if required tools are installed
atl status
```

## 📋 **Common Workflows**

### Development Workflow

```bash
# 1. Check status and lint code
atl status
atl lint --fix

# 2. Plan and apply to development
atl plan --environment development
atl apply --environment development

# 3. Generate documentation
atl docs build
```

### Production Deployment

```bash
# 1. Validate everything
atl quality lint --strict
atl infra check

# 2. Plan for production
atl infra plan --environment production

# 3. Apply with approval
atl infra apply --environment production --auto-approve
```

### Domain Deployment

```bash
# 1. Deploy specific domain
atl apply --target domain --domain-name myapp.allthingslinux.dev

# 2. Enable domain
atl infra enable myapp.allthingslinux.dev

# 3. Verify configuration
atl infra config
```

The unified `atl` CLI provides a consistent, powerful interface for all infrastructure operations!
