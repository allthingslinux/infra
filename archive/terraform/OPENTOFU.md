# OpenTofu Infrastructure for All Things Linux

This directory contains the OpenTofu configuration for managing All Things Linux infrastructure on Hetzner Cloud.

## Why OpenTofu?

- 100% Open Source
- Compatible with Terraform modules and providers
- Community-driven development
- No license restrictions

## Getting Started

### Prerequisites

1. Install OpenTofu:
   ```bash
   ./scripts/install_opentofu.sh
   ```

2. Set up your environment variables:
   ```bash
   # Create a .env file
   cp .env.example .env
   # Edit with your details
   nano .env
   ```

### Directory Structure

```
terraform/
├── modules/           # Reusable modules
│   ├── network/      # Network configuration
│   ├── server/       # Server configurations
│   └── firewall/     # Firewall rules
├── environments/     # Environment-specific configs
│   ├── dev/         # Development environment
│   └── prod/        # Production environment
└── scripts/         # Utility scripts
```

## Usage

### Initialize

```bash
cd environments/dev
tofu init
```

### Plan Changes

```bash
tofu plan -var-file=terraform.tfvars
```

### Apply Changes

```bash
tofu apply -var-file=terraform.tfvars
```

### Destroy Resources

```bash
tofu destroy -var-file=terraform.tfvars
```

## Environment Variables

Create a `.env` file with:

```env
HCLOUD_TOKEN=your_hetzner_token
SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa.pub)"
```

## Modules

### Network Module
Manages VPC, subnets, and routing.

### Server Module
Creates and configures Hetzner Cloud servers.

### Firewall Module
Manages network security groups and rules.

## Best Practices

1. **Version Control**:
   - Never commit sensitive data
   - Use `.gitignore` to exclude state files

2. **State Management**:
   - Consider remote state storage
   - Enable state locking

3. **Variables**:
   - Use variables for all configurable values
   - Define sensible defaults
   - Mark sensitive variables

## Next Steps

1. Set up remote state storage
2. Configure CI/CD pipelines
3. Add monitoring and alerts

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your Hetzner Cloud token
2. **Network Issues**: Check VPC and security group settings
3. **State Locking**: Manually unlock if needed with `tofu force-unlock LOCK_ID`

## License

This project is open source and available under the [MIT License](LICENSE).
