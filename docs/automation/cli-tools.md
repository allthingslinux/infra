# CLI Tools

All Things Linux infrastructure operations are managed through the **unified `atl` CLI**, providing a consistent interface for all tools and operations.

## 🚀 **CI/CD Automation System**

The project includes a comprehensive, industry-standard CI/CD system built around three optimized GitHub workflows:

### **Workflow Overview**

| Workflow | Purpose | Triggers | Key Features |
|----------|---------|----------|-------------|
| **CI** | Quality assurance & testing | Push, PR, Manual | Parallel jobs, path filtering, comprehensive caching |
| **Security** | Security scanning | Push, PR, Weekly, Manual | Multi-scanner approach, SARIF reporting |
| **PR Automation** | PR analysis & labeling | PR events | Size analysis, complexity scoring, auto-assignment |
| **Labeler** | Path-based labeling | PR file changes | Sophisticated domain classification |

### **CI Workflow Features**

```yaml
# Optimized job execution with dependencies
Quick Checks → Python Quality → Python Tests
            ↘ Terraform Quality
            ↘ Ansible Quality
            ↘ Documentation
            ↘ Integration Tests → Quality Gate
```

**Capabilities**:

- **Smart Path Filtering**: Only runs relevant checks based on changed files
- **Advanced Caching**: UV cache, Terraform providers, dependency caching
- **Parallel Execution**: Multiple jobs run simultaneously for speed
- **Comprehensive Reporting**: Detailed summaries and status aggregation

### **Security Integration**

The security workflow provides enterprise-grade scanning:

- **Secrets Detection**: Gitleaks with custom configuration
- **Dependency Scanning**: OWASP vulnerability assessment
- **Infrastructure Security**: Terraform scanning with Trivy
- **Static Analysis**: CodeQL for code security analysis
- **Container Security**: Docker image vulnerability scanning

### **PR Automation Intelligence**

The PR automation system provides intelligent analysis:

```bash
# Automatic PR Classification
Size: XS/S/M/L/XL (based on line changes)
Complexity: Scored analysis (infrastructure files weighted higher)
Security Impact: Detects security-sensitive changes
Conflicts: Automatic merge conflict detection
```

**Smart Assignment**: Auto-assigns reviewers based on:

- File paths changed (via labeler)
- Security impact
- Complexity score
- Domain expertise mapping

### **Local Development Integration**

Pre-commit hooks complement the CI system:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run specific checks
uv run pre-commit run --hook-stage manual ansible-lint
uv run pre-commit run --all-files

# Test before push
atl quality lint --fix
```

## 🎯 **Unified ATL CLI**

### Overview

The `atl` CLI consolidates all infrastructure operations into a single, well-organized command-line tool:

```bash
atl <group> <command> [options]
```

### Design Philosophy

The unified CLI follows modern DevOps principles:

- **🎯 Single Entry Point**: One command to rule them all - no more remembering multiple CLI tools
- **📊 Organized Structure**: Commands grouped by logical function (infra, quality, docs, utils)
- **⚡ Quick Access**: Most common operations available at the top level (`atl plan`, `atl apply`, `atl lint`)
- **🔍 Discoverable**: Built-in help system with `atl info` and comprehensive `--help` options
- **🚀 Developer Experience**: Consistent interface, rich output, and intuitive commands
- **🔧 Automation Friendly**: Designed for both interactive use and CI/CD pipelines

### Command Groups

#### **Infrastructure Management (`atl infra`)**

Terraform and Ansible operations for infrastructure lifecycle management:

```bash
atl infra plan              # Plan infrastructure changes
atl infra apply             # Apply infrastructure changes
atl infra destroy           # Destroy infrastructure
atl infra check             # Run syntax checks
atl infra enable domain.com # Enable a domain
atl infra disable domain.com # Disable a domain
atl infra config            # Show current configuration
```

#### **Quality Assurance (`atl quality`)**

Code quality, linting, and validation:

```bash
atl quality lint                    # Run all linting checks
atl quality lint --target playbooks # Lint specific target
atl quality lint --fix             # Auto-fix issues where possible
atl quality lint --strict          # Fail on warnings
```

#### **Documentation (`atl docs`)**

Documentation generation and diagram creation:

```bash
atl docs build                     # Build documentation
atl docs build --serve             # Build and serve locally
atl docs diagrams                  # Generate infrastructure diagrams
atl docs diagrams --format png     # Generate PNG diagrams
```

#### **Utilities (`atl utils`)**

Maintenance and utility operations:

```bash
atl utils update-collections       # Update Ansible collections
atl utils update-collections --force # Force update
```

### Quick Access Commands

For frequently used operations, quick access commands are available at the top level:

```bash
atl plan                           # Equivalent to: atl infra plan
atl apply                          # Equivalent to: atl infra apply
atl lint                           # Equivalent to: atl quality lint
```

### Global Options

Most commands support these global options:

- `--environment, -e`: Target environment (development/staging/production)
- `--verbose, -v`: Enable verbose output
- `--dry-run, -d`: Show what would be changed without making changes
- `--help`: Show detailed help for any command

### Examples

#### Basic Infrastructure Operations

```bash
# Plan changes for development environment
atl plan --environment development

# Apply changes with auto-approval for staging
atl apply --environment staging --auto-approve

# Run syntax checks
atl infra check

# Destroy development infrastructure
atl infra destroy --environment development
```

#### Domain Management

```bash
# Enable a new domain
atl infra enable myapp.allthingslinux.dev

# Disable a domain
atl infra disable old.allthingslinux.dev

# Deploy specific domain with Ansible only
atl apply --target domain --domain-name myapp.allthingslinux.dev --ansible-only
```

#### Quality and Documentation

```bash
# Run comprehensive linting
atl quality lint --verbose

# Auto-fix linting issues
atl quality lint --fix

# Build and serve documentation locally
atl docs build --serve --port 8080

# Generate infrastructure diagrams
atl docs diagrams --output-dir assets/diagrams
```

#### Maintenance

```bash
# Update Ansible collections
atl utils update-collections

# Check tool availability
atl status

# Show all available commands
atl info
```

## 🔧 **Help and Discovery**

### Getting Help

```bash
atl --help                         # Show main help
atl info                          # Show organized command overview
atl status                        # Check tool availability
atl <group> --help                # Show group-specific help
atl <group> <command> --help      # Show detailed command help
```

### Command Discovery

The CLI is designed for discoverability:

1. **Start with `atl info`
