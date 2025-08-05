# All Things Linux Infrastructure

This directory contains the infrastructure as code for All Things Linux services.

## Structure

- `ansible/` - Configuration management
- `terraform/` - Infrastructure provisioning
- `scripts/` - Utility scripts
- `docs/` - Documentation

## Getting Started

1. Install dependencies:
   ```bash
   # Install OpenTofu
   ./scripts/install_opentofu.sh
   ```

2. Set up your environment:
   ```bash
   cd terraform/environments/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your configuration
   ```

3. Deploy infrastructure:
   ```bash
   tofu init
   tofu plan
   tofu apply
   ```
