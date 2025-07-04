# CLI Tools

All Things Linux infrastructure operations are managed through the **unified `atl` CLI**, providing a consistent interface for all tools and operations.

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

1. **Start with `atl info`** to see all available command groups
2. **Use `atl <group> --help`** to explore specific groups
3. **Use `atl <command> --help`** for detailed command options
4. **Use `atl status`** to verify tool prerequisites

## 🛠 **Installation**

The unified CLI is automatically available after installing the project:

```bash
# Install project dependencies
poetry install

# Verify CLI availability
atl status

# Get started
atl info
```

## 🏗 **Integration**

### CI/CD Integration

The unified CLI is designed for CI/CD pipelines:

```bash
# In CI/CD scripts
atl plan --environment production
atl apply --environment production --auto-approve
atl quality lint --strict
```

### Development Workflow

Typical development workflow:

```bash
# 1. Check current status
atl status

# 2. Plan changes
atl plan --verbose

# 3. Run quality checks
atl quality lint

# 4. Apply changes
atl apply

# 5. Update documentation
atl docs build
```

The unified CLI provides a consistent, discoverable interface that scales from simple operations to complex infrastructure management workflows.

## 🎉 **Benefits Over Previous Approach**

### Before: Multiple Separate Tools

```bash
# Old approach - multiple commands to remember
atl-deploy plan
atl-lint --fix
atl-docs --serve
atl-update-collections
atl-diagrams
```

### After: Unified Interface

```bash
# New approach - single, organized interface
atl plan                    # Quick access
atl lint --fix             # Quick access
atl docs build --serve     # Organized
atl utils update-collections  # Organized
atl docs diagrams          # Organized
```

### Key Improvements

1. **🎯 Single Entry Point**: One `atl` command instead of 5+ separate tools
2. **📊 Better Organization**: Logical grouping by function (infra, quality, docs, utils)
3. **🔍 Enhanced Discovery**: `atl info` shows all commands organized by category
4. **⚡ Quick Access**: Common operations available at top level
5. **🛠 Better Help**: Comprehensive help system with examples
6. **🚀 Consistent Interface**: Same options and patterns across all commands
7. **📈 Future-Proof**: Easy to add new functionality without creating new top-level commands

## 🏁 **Quick Reference**

### Most Common Commands

```bash
# Planning and deployment
atl plan                    # Plan changes
atl apply                   # Apply changes
atl infra destroy           # Destroy infrastructure

# Quality assurance
atl lint                    # Run linting
atl lint --fix              # Fix issues
atl quality lint --strict   # Strict linting

# Documentation
atl docs build --serve      # Build and serve docs
atl docs diagrams          # Generate diagrams

# Maintenance
atl utils update-collections  # Update collections
```

### Discovery Commands

```bash
atl info                    # Show all commands organized by category
atl status                  # Check tool availability
atl <command> --help        # Detailed help for any command
```

The unified `atl` CLI provides a modern, consistent interface that scales from quick interactive use to complex automation workflows!
