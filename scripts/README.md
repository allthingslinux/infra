# ATL Infrastructure Scripts

This directory contains the unified command-line interface (CLI) and supporting tools for All Things Linux infrastructure management.

## Directory Structure

```
scripts/
├── cli.py                 # Main CLI entry point (atl command)
├── commands/              # Command implementations
│   ├── __init__.py       # Commands package
│   ├── deploy.py         # Infrastructure deployment commands
│   ├── lint.py           # Code quality and linting commands
│   ├── docs.py           # Documentation generation commands
│   ├── diagrams.py       # Infrastructure diagram generation
│   └── update_collections.py # Ansible collection management
├── common/               # Shared utilities
│   ├── config.py         # Configuration management
│   └── logging.py        # Logging utilities with auto-cleanup
├── setup/                # Environment setup scripts
│   ├── setup-cloudflare.sh  # Cloudflare CLI setup
│   ├── setup-hooks.sh       # Git hooks installation
│   ├── setup-uv.sh          # uv and dependency setup
│   └── setup-terraform.sh   # Terraform installation
└── README.md             # This file
```

## Architecture

### Main CLI (`cli.py`)

The main entry point that provides a unified interface for all infrastructure operations. It organizes commands into logical groups and provides both grouped commands and quick access shortcuts.

### Command Implementations (`commands/`)

Each command module provides specific functionality:

- **`deploy.py`**: Infrastructure deployment using Terraform and Ansible
- **`lint.py`**: Code quality validation and linting
- **`docs.py`**: Documentation generation using MkDocs
- **`diagrams.py`**: Infrastructure diagram generation
- **`update_collections.py`**: Ansible collection management

### Shared Utilities (`common/`)

Common functionality used across multiple commands:

- **`config.py`**: Configuration file management and validation
- **`logging.py`**: Rich console output and automatic log file cleanup

### Setup Scripts (`setup/`)

Environment setup and dependency installation scripts for development and deployment.

## Unified CLI Design

The ATL CLI follows a hierarchical command structure:

```bash
atl <group> <command> [options]    # Grouped commands
atl <command> [options]            # Quick access commands
```

### Command Groups

- **`infra`**: Infrastructure management (Terraform + Ansible)
- **`quality`**: Code quality validation and linting
- **`docs`**: Documentation and diagram generation
- **`utils`**: Utility and maintenance operations

### Quick Access Commands

Common operations available directly at the top level:

- **`plan`**: Plan infrastructure changes
- **`apply`**: Apply infrastructure changes
- **`lint`**: Run quality checks

## Development Guidelines

### Adding New Commands

1. **Create command module** in `scripts/commands/`:

   ```python
   # commands/my_command.py
   import click
   from ..common.logging import InfraLogger
   from ..common.config import ConfigManager

   @click.command()
   def cli():
       """My new command"""
       pass
   ```

2. **Register in main CLI** (`cli.py`):

   ```python
   from .commands.my_command import cli as my_command
   group.add_command(my_command, name="my-command")
   ```

3. **Update documentation** in `info()` command and README

### Import Guidelines

- **From commands to common**: Use `..common.module` (parent directory)
- **From cli to commands**: Use `.commands.module` (subdirectory)
- **External imports**: Standard Python import paths

### Logging and Cleanup

All commands automatically get:

- Rich console output with consistent styling
- Automatic log file generation with timestamps
- Automatic cleanup of old log files (keeps 5 recent per tool, max 7 days)
- Error handling and progress reporting

## Command Reference

### Infrastructure Commands

```bash
atl infra plan              # Plan infrastructure changes
atl infra apply             # Apply infrastructure changes
atl infra destroy           # Destroy infrastructure
```

### Quality Commands

```bash
atl quality lint            # Run comprehensive linting
atl quality lint --fix      # Auto-fix issues where possible
```

### Documentation Commands

```bash
atl docs build              # Generate all documentation
atl docs build --serve      # Generate and serve locally
atl docs diagrams           # Generate infrastructure diagrams
```

### Utility Commands

```bash
atl utils update-collections     # Update Ansible collections
atl utils cleanup-logs          # Clean up old log files
atl utils cleanup-logs --dry-run # Preview cleanup
```

### Discovery Commands

```bash
atl info                    # Show available commands
atl status                  # Check tool dependencies
```

## Log Management

The CLI automatically manages log files to prevent clutter:

### Automatic Cleanup

- Runs on every command execution
- Keeps 5 most recent log files per tool type
- Removes logs older than 7 days
- Safe operation (never removes active logs)

### Manual Cleanup

```bash
atl utils cleanup-logs                    # Use defaults
atl utils cleanup-logs --max-files 10     # Keep 10 files per tool
atl utils cleanup-logs --max-age 14       # Keep files for 14 days
atl utils cleanup-logs --dry-run          # Preview what would be cleaned
```

### Log Organization

```
logs/
├── deploy-20240704_052731.log    # Infrastructure deployment
├── docs-20240704_052420.log      # Documentation generation
├── lint-20240703_222915.log      # Quality checks
└── ...                           # Other tool logs
```

## Testing

Test the CLI functionality:

```bash
# Test main functionality
atl --help                  # Main help
atl info                    # Command overview
atl status                  # Tool availability

# Test command groups
atl infra --help           # Infrastructure commands
atl quality --help         # Quality commands
atl docs --help            # Documentation commands
atl utils --help           # Utility commands

# Test specific commands
atl plan --help            # Quick plan command
atl utils cleanup-logs --dry-run  # Log cleanup preview
```

## Benefits of This Architecture

1. **Clean Organization**: Commands separated from orchestration logic
2. **Scalable**: Easy to add new commands without cluttering main directory
3. **Maintainable**: Clear separation of concerns between CLI and implementations
4. **Discoverable**: Hierarchical structure with logical groupings
5. **Flexible**: Both grouped commands and quick access patterns
6. **Self-Managing**: Automatic log cleanup prevents directory clutter

This structure scales from simple interactive use to complex automation workflows while maintaining clarity and ease of maintenance.
