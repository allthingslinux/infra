# Terraform Configuration

## Overview

This document explains the proper Terraform directory structure and configuration to prevent scattered `.terraform` directories and ensure efficient plugin caching.

## Directory Structure

### 🎯 **Root Modules** (Where you run `terraform init`)

```text
terraform/
├── main.tf                           # Main terraform root
├── variables.tf
├── outputs.tf
└── environments/
    ├── development/                  # Development environment root
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── staging/                      # Staging environment root
    │   └── ...
    └── production/                   # Production environment root
        └── ...
```

### 🚫 **Modules** (Reusable components - NEVER run `terraform init` here)

```text
terraform/modules/
├── compute/                          # Reusable compute module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── network/                          # Reusable network module
│   └── ...
└── security/                        # Reusable security module
    └── ...
```

## Centralized Configuration

### Project-Specific Configuration

Terraform is configured to use project-local directories for all operations via `.terraformrc`:

```hcl
# Project-specific Terraform CLI Configuration
plugin_cache_dir = "$TF_PLUGIN_CACHE_DIR"
```

The ATL CLI automatically centralizes all terraform operations in a single unified directory:

- **Unified Directory**: `.terraform/` (contains everything terraform-related)
  - `.terraform/cache/` (plugin cache shared across all operations)
  - `.terraform/data/` (terraform working data - providers, modules, state)

### Benefits

1. **Complete centralization** - All terraform data in project root
2. **Prevents scattered directories** - No `.terraform` directories anywhere else
3. **Faster initialization** - plugins are downloaded once and reused
4. **Saves disk space** - no duplicate plugin downloads
5. **Cleaner repository** - single location for all terraform data
6. **No provider duplication** - separate cache and data directories prevent duplicates

### How It Works

1. **TF_CLI_CONFIG_FILE** - Points to project-specific `.terraformrc`
2. **TF_PLUGIN_CACHE_DIR** - Points to `.terraform/cache/` (plugin cache)
3. **TF_DATA_DIR** - Points to `.terraform/data/` (terraform working data)
4. **All operations** - Use single unified directory regardless of working directory

## Usage Guidelines

### ✅ **Correct Usage with ATL CLI**

```bash
# Use the integrated CLI (recommended)
atl deploy plan -e development
atl deploy apply -e development

# Direct terraform usage (if needed)
cd terraform/environments/development/
terraform init
terraform plan
terraform apply
```

### ❌ **Incorrect Usage**

```bash
# NEVER do this - modules are reusable components, not root modules
cd terraform/modules/compute/
terraform init  # ❌ This will create unnecessary .terraform directories
```

## Troubleshooting

### Cleaning Up Existing `.terraform` Directories

If you have existing `.terraform` directories in modules, clean them up:

```bash
# Remove .terraform directories from modules
find terraform/modules -name ".terraform" -type d -exec rm -rf {} +

# Reinitialize from proper root directories
cd terraform/environments/development/
terraform init
```

### Verifying Plugin Cache

Check that the unified terraform directory is working:

```bash
# Check unified terraform directory
ls -la .terraform/
ls -la .terraform/cache/

# Run deployment and verify it uses unified structure
atl deploy plan -e development --terraform-only
```

### Directory Locations

All terraform data is centralized in a single unified directory:

- **Unified Directory**: `.terraform/` (everything terraform-related)
  - **Plugin Cache**: `.terraform/cache/` (shared provider plugins)
  - **Working Data**: `.terraform/data/` (terraform working directory data)
    - `.terraform/data/providers/` (provider installations)
    - `.terraform/data/modules/` (module installations)
    - `.terraform/data/terraform.tfstate` (when using local backend)
- **Benefits**: Complete unification, team consistency, no scattered files, no provider duplication

## Best Practices

1. **Use the ATL CLI** - Prefer `atl deploy` over direct terraform commands
2. **Only initialize root modules** - Never run `terraform init` in modules
3. **Use project-specific caching** - `.terraformrc` is automatically configured
4. **Clean up periodically** - Remove old cached plugins from `.terraform/cache/`
5. **Document structure** - Make it clear which directories are roots vs modules
6. **Use version constraints** - Pin provider versions in your configurations

## Related Documentation

- [Terraform CLI Configuration](https://developer.hashicorp.com/terraform/cli/config/config-file)
- [Plugin Cache](https://developer.hashicorp.com/terraform/cli/config/config-file#plugin-cache)
- [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
