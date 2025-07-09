# Configuration Guide

This guide covers the initial configuration needed to start using the All Things Linux infrastructure.

## 🔐 SSH Key Setup

### Generate SSH Keys

If you don't have SSH keys configured:

```bash
# Generate a new SSH key for infrastructure access
ssh-keygen -t ed25519 -f ~/.ssh/atl_infrastructure -C "your-email@example.com"

# Or use RSA if ed25519 isn't supported
ssh-keygen -t rsa -b 4096 -f ~/.ssh/atl_infrastructure -C "your-email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/atl_infrastructure
```

### Configure SSH Client

Add to your `~/.ssh/config`:

```bash
# All Things Linux Infrastructure
Host atl-*
    User root
    IdentityFile ~/.ssh/atl_infrastructure
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Environment-specific configurations
Host *.development.allthingslinux.org
    User root
    IdentityFile ~/.ssh/atl_infrastructure

Host *.staging.allthingslinux.org
    User root
    IdentityFile ~/.ssh/atl_infrastructure

Host *.allthingslinux.org
    User root
    IdentityFile ~/.ssh/atl_infrastructure
```

## 🌍 Environment Variables

### Required Variables

Create a `.env` file or add to your shell profile:

```bash
# Hetzner Cloud API Token (required for infrastructure)
export HCLOUD_TOKEN="your-hetzner-cloud-api-token"

# Cloudflare API Token (required for DNS)
export CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"

# Environment selection (development, staging, production)
export ATL_ENVIRONMENT="development"

# Optional: Terraform workspace override
export TF_WORKSPACE="development"
```

### Getting API Tokens

#### Hetzner Cloud Token

1. Go to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select your project (or create one)
3. Navigate to **Security** → **API Tokens**
4. Click **Generate API Token**
5. Select **Read & Write** permissions
6. Copy the token (you won't see it again!)

#### Cloudflare API Token

1. Go to [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click **Create Token**
3. Use **Custom token** with these permissions:
   - **Zone**: `Zone:Read` (all zones)
   - **Zone**: `Zone Settings:Edit` (specific zone)
   - **DNS**: `DNS:Edit` (specific zone)
4. Set zone resources to include your domain
5. Copy the token

### Environment Persistence

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# All Things Linux Infrastructure
export HCLOUD_TOKEN="your-token-here"
export CLOUDFLARE_API_TOKEN="your-token-here"
export ATL_ENVIRONMENT="development"

# Add SSH key on shell startup
ssh-add ~/.ssh/atl_infrastructure 2>/dev/null
```

## 📁 Project Configuration

### Ansible Configuration

The project includes `ansible.cfg` with optimized settings:

```ini
[defaults]
inventory = inventories/dynamic.py
host_key_checking = False
pipelining = True
forks = 10
strategy = mitogen_linear

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

You can override settings in your local environment if needed.

### Git Configuration

Set up Git hooks for code quality:

```bash
# Initialize pre-commit hooks
./scripts/setup-hooks.sh

# Configure Git user (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 🎯 Domain Configuration

### Understanding domains.yml

The `domains.yml` file is the single source of truth for your infrastructure:

```yaml
domains:
  example_service:
    enabled: true                    # Deploy this service
    domain: "example.allthingslinux.org"

    # Server configuration
    server:
      type: "cx21"                   # Hetzner server type
      location: "ash"                # Hetzner location
      count: 1                       # Number of servers

    # Services to install
    services:
      - docker
      - nginx
      - custom-app

    # DNS subdomains
    subdomains:
      - api
      - admin

    # Optional features
    features:
      ssl: true
      backup: true

    # Monitoring
    monitoring:
      enabled: true
```

### Environment-Specific Configuration

The same `domains.yml` works across environments with automatic adjustments:

- **Development**: `.development.allthingslinux.org` subdomains
- **Staging**: `.staging.allthingslinux.org` subdomains
- **Production**: Direct domain names

## ✅ Verify Configuration

### Test Environment Variables

```bash
# Check if tokens are set
echo "Hetzner: ${HCLOUD_TOKEN:0:10}..."
echo "Cloudflare: ${CLOUDFLARE_API_TOKEN:0:10}..."

# Test API access
curl -H "Authorization: Bearer $HCLOUD_TOKEN" \
     https://api.hetzner.cloud/v1/servers

curl -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     https://api.cloudflare.com/client/v4/user/tokens/verify
```

### Test SSH Configuration

```bash
# Check SSH agent
ssh-add -l

# Test key loading
ssh-add ~/.ssh/atl_infrastructure

# Verify configuration
ssh -T git@github.com  # Should show your GitHub username
```

### Test Project Configuration

```bash
# Verify Ansible configuration
ansible-config dump

# Test dynamic inventory
./scripts/deploy-dynamic.sh config

# Run configuration validation
./scripts/lint.sh
```

## 🛠️ Optional Configuration

### Shell Aliases

Add helpful aliases to your shell profile:

```bash
# All Things Linux Infrastructure aliases
alias atl-dev='export ATL_ENVIRONMENT=development'
alias atl-staging='export ATL_ENVIRONMENT=staging'
alias atl-prod='export ATL_ENVIRONMENT=production'

alias atl-plan='atl plan'
alias atl-deploy='atl apply'
alias atl-config='atl config'
alias atl-lint='atl lint'

# Quick deployment aliases
alias atl-infra='./scripts/deploy-dynamic.sh infrastructure'
alias atl-all='./scripts/deploy-dynamic.sh all'
```

### Tmux/Screen Setup

For long-running deployments:

```bash
# Create a dedicated tmux session
tmux new-session -d -s atl-infra

# Or use screen
screen -S atl-infra
```

### IDE Integration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "ansible.python.interpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "yaml.schemas": {
    "./schemas/domains.json": "domains.yml"
  },
  "files.associations": {
    "*.yml": "ansible",
    "*.yaml": "ansible"
  }
}
```

#### Terminal Integration

For better terminal experience:

```bash
# Add to shell profile for project directory shortcuts
export ATL_INFRA_DIR="$HOME/dev/allthingslinux/infra"
alias atl-cd='cd $ATL_INFRA_DIR'

# Auto-activate uv environment when entering directory
if [[ "$PWD" == "$ATL_INFRA_DIR"* ]]; then
    source .venv/bin/activate 2>/dev/null || true
fi
```

## 🚨 Security Considerations

### Token Security

- **Never commit tokens** to git repositories
- **Use different tokens** for different environments
- **Rotate tokens regularly** (quarterly recommended)
- **Use read-only tokens** when possible
- **Store tokens securely** (password manager, encrypted storage)

### SSH Security

- **Use strong passphrases** for SSH keys
- **Limit SSH key access** to necessary servers only
- **Regularly audit** SSH key usage
- **Use SSH agent forwarding** carefully

### Environment Isolation

- **Never deploy to production** from development environment
- **Use separate API tokens** for each environment
- **Test in staging** before production deployments
- **Monitor environment variables** in deployment logs

## 🚨 Troubleshooting

### Common Configuration Issues

#### Environment variables not loaded

```bash
# Check current environment
env | grep -E "(HCLOUD|CLOUDFLARE|ATL)"

# Reload shell profile
source ~/.bashrc  # or ~/.zshrc

# Verify in new shell
bash -c 'echo $HCLOUD_TOKEN'
```

#### SSH key issues

```bash
# Debug SSH connection
ssh -vvv root@server-ip

# Check SSH agent
ssh-add -l

# Re-add keys
ssh-add ~/.ssh/atl_infrastructure
```

#### API token validation

```bash
# Test Hetzner token
curl -H "Authorization: Bearer $HCLOUD_TOKEN" \
     https://api.hetzner.cloud/v1/servers \
     | jq .

# Test Cloudflare token
curl -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     https://api.cloudflare.com/client/v4/user/tokens/verify \
     | jq .
```

#### Ansible configuration

```bash
# Check ansible configuration
ansible-config view

# Test inventory
ansible-inventory --list

# Debug connection
ansible all -m ping -vvv
```

## 📝 Next Steps

After completing configuration:

1. **[Deployment Guide](../guides/deployment.md)** - Deploy your first environment
2. **[Infrastructure Guide](../guides/infrastructure.md)** - Learn infrastructure management
3. **[Development Workflow](../guides/development.md)** - Understand the development process

## 📚 Additional Resources

- [Hetzner Cloud API Documentation](https://docs.hetzner.cloud/)
- [Cloudflare API Documentation](https://developers.cloudflare.com/api/)
- [Ansible Configuration Reference](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)
- [SSH Configuration Guide](https://www.ssh.com/academy/ssh/config)
