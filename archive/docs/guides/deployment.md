# Deployment Guide

This guide covers how to deploy infrastructure and services using the All Things Linux unified deployment system.

## 🎯 Overview

Our deployment system uses a **single unified script** that handles both Terraform (infrastructure) and Ansible (configuration) operations through one interface, with all configuration managed in `domains.yml`.

### Key Scripts

- `./scripts/deploy.sh` - **NEW** Unified deployment interface (replaces all old deployment scripts)
- `./scripts/lint.sh` - Code quality validation
- `./scripts/setup-hooks.sh` - Development environment setup
- `./scripts/setup-uv.sh` - uv environment setup
- `./scripts/setup-cloudflare.sh` - Cloudflare API configuration

### Consolidated Approach

**Before (deprecated):**

- `deploy-dynamic.sh`
- `deploy-dynamic-domains.sh`
- `deploy-uv.sh`
- `terraform-deploy.sh`

**After (current):**

- `deploy.sh` - Single script with all functionality

### Deployment Workflow

1. **Plan** - Preview changes without applying
2. **Validate** - Run linting and quality checks
3. **Deploy** - Apply infrastructure and configuration changes
4. **Verify** - Confirm deployment success

## 🚀 Quick Start Deployment

### 1. First-Time Setup

```bash
# Setup environment
./scripts/setup-uv.sh            # Install dependencies
./scripts/setup-hooks.sh         # Configure git hooks

# Configure cloud services (one-time)
export HCLOUD_TOKEN="your-token"
export CLOUDFLARE_API_TOKEN="your-token"
./scripts/setup-cloudflare.sh   # Guided Cloudflare setup

# Test configuration
./scripts/deploy.sh config
```

### 2. Deploy Development Environment

```bash
# Plan infrastructure changes (preview)
./scripts/deploy.sh plan all

# Deploy infrastructure only
./scripts/deploy.sh apply infrastructure

# Deploy all enabled domains
./scripts/deploy.sh apply all
```

### 3. Verify Deployment

```bash
# Check current configuration
./scripts/deploy.sh config

# Test connectivity
ansible all -i inventories/dynamic.py -m ping
```

## 📋 Deployment Commands

### Infrastructure Management

```bash
# Plan infrastructure changes
./scripts/deploy.sh plan infrastructure

# Apply infrastructure changes
./scripts/deploy.sh apply infrastructure

# Destroy infrastructure (careful!)
./scripts/deploy.sh destroy infrastructure

# Plan with specific environment
./scripts/deploy.sh plan infrastructure -e staging
```

### Domain Deployment

```bash
# Deploy a specific domain
./scripts/deploy.sh apply domain atl_wiki

# Deploy with verbose output
./scripts/deploy.sh apply domain atl_tools -v

# Dry-run deployment (preview changes)
./scripts/deploy.sh apply domain atl_dev -d

# Deploy all domains
./scripts/deploy.sh apply domains
```

### Bulk Operations

```bash
# Deploy everything (infrastructure + domains)
./scripts/deploy.sh apply all

# Plan everything first
./scripts/deploy.sh plan all

# Deploy only Ansible configuration
./scripts/deploy.sh apply all --ansible-only

# Deploy only Terraform infrastructure
./scripts/deploy.sh apply all --terraform-only
```

### Domain Management

```bash
# Enable a domain
./scripts/deploy.sh enable atl_chat

# Disable a domain
./scripts/deploy.sh disable atl_dev

# Show current configuration
./scripts/deploy.sh config
```

## 🌍 Environment-Specific Deployment

### Development Environment

```bash
# Deploy to development (default)
./scripts/deploy.sh plan all

# Deploy infrastructure
./scripts/deploy.sh apply infrastructure

# Deploy all services
./scripts/deploy.sh apply all
```

**Development Features:**

- Smaller server types (cx11, cx21)
- Direct IP access (no load balancer)
- Relaxed security settings
- Debug logging enabled

### Staging Environment

```bash
# Deploy to staging environment
./scripts/deploy.sh plan all -e staging

# Deploy infrastructure with load balancer
./scripts/deploy.sh apply infrastructure -e staging

# Deploy all services
./scripts/deploy.sh apply all -e staging
```

**Staging Features:**

- Production-like infrastructure
- Load balancer enabled
- SSL with staging certificates
- Performance monitoring

### Production Environment

```bash
# Always plan first in production
./scripts/deploy.sh plan all -e production

# Apply with confirmation (will prompt)
./scripts/deploy.sh apply infrastructure -e production

# Auto-approve (use with extreme caution)
./scripts/deploy.sh apply all -e production -y
```

**Production Features:**

- High-availability infrastructure
- Multiple server redundancy
- Full monitoring and alerting
- Strict security policies
- Automated backups

## 🔧 Advanced Deployment Options

### Quality Checks

```bash
# Run linting before deployment
./scripts/deploy.sh lint

# Check syntax only
./scripts/deploy.sh check

# Verbose deployment with all output
./scripts/deploy.sh apply all -v

# Dry-run to preview changes
./scripts/deploy.sh apply all -d
```

### Specialized Operations

```bash
# Infrastructure only (skip Ansible)
./scripts/deploy.sh apply infrastructure --terraform-only

# Configuration only (skip Terraform)
./scripts/deploy.sh apply all --ansible-only
  --inventory inventories/custom.yml

# Override environment settings
./scripts/deploy-dynamic.sh all \
  --extra-vars "environment=custom"
```

### Selective Deployment

```bash
# Deploy only specific roles
./scripts/deploy-dynamic.sh all --tags "docker,nginx"

# Skip certain components
./scripts/deploy-dynamic.sh all --skip-tags "backup,monitoring"

# Deploy to specific hosts
./scripts/deploy-dynamic.sh all --limit "web_servers"

# Deploy with specific strategy
./scripts/deploy-dynamic.sh all --extra-vars "strategy=free"
```

### Debug and Testing

```bash
# Enable verbose output
./scripts/deploy-dynamic.sh domain atl_tools --verbose

# Run syntax check only
./scripts/deploy-dynamic.sh all --syntax-check

# List all tasks without execution
./scripts/deploy-dynamic.sh all --list-tasks

# Check what hosts would be affected
./scripts/deploy-dynamic.sh all --list-hosts
```

## ✅ Pre-Deployment Validation

### Code Quality Checks

```bash
# Run all linting checks
./scripts/lint.sh

# Run specific checks
./scripts/lint.sh --ansible-lint
./scripts/lint.sh --yamllint
./scripts/lint.sh --terraform

# Auto-fix common issues
./scripts/lint.sh --fix

# Run lefthook hooks
uv run lefthook run pre-commit --all-files
```

### Infrastructure Validation

```bash
# Plan changes without applying
./scripts/deploy-dynamic.sh infrastructure plan

# Validate Terraform configuration
cd terraform && terraform validate

# Check Ansible syntax
ansible-playbook --syntax-check playbooks/dynamic-deploy.yml

# Test dynamic inventory
ansible-inventory -i inventories/dynamic.py --list
```

### Connectivity Testing

```bash
# Test SSH connectivity
ansible all -i inventories/dynamic.py -m ping

# Test specific groups
ansible web_servers -i inventories/dynamic.py -m ping

# Check system status
ansible all -i inventories/dynamic.py -a "uptime"
```

## 📋 Daily Operations Checklist

### Morning Health Check

Perform these checks to ensure system health:

```bash
# Check server health
ansible all -i inventories/dynamic.py -a "uptime"

# Check disk space
ansible all -i inventories/dynamic.py -a "df -h"

# Check memory usage
ansible all -i inventories/dynamic.py -a "free -m"

# Check service status
./scripts/deploy-dynamic.sh config

# Review logs for errors
ansible web_servers -i inventories/dynamic.py \
  -a "journalctl --since '24 hours ago' --priority=err"

# Verify backups completed
ansible backup_servers -i inventories/dynamic.py \
  -a "ls -la /opt/backups/ | head -10"
```

### Pre-Deployment Checklist

Before any deployment:

- [ ] Test in staging environment first
- [ ] Run dry-run deployment: `./scripts/deploy-dynamic.sh all --dry-run`
- [ ] Review changes with team
- [ ] Schedule maintenance window if needed
- [ ] Notify community for major changes
- [ ] Prepare rollback plan

### Post-Deployment Checklist

After deployment:

- [ ] Verify all services are running
- [ ] Check application functionality
- [ ] Monitor logs for errors: `./scripts/deploy-dynamic.sh all --tags logging`
- [ ] Run connectivity tests
- [ ] Update documentation if needed
- [ ] Monitor performance metrics

## 🚨 Emergency Procedures

### Quick Emergency Response

#### Service Down Emergency

```bash
# 1. Quick status check
./scripts/deploy-dynamic.sh config

# 2. Check what's running
ansible all -i inventories/dynamic.py -a "docker compose ps"

# 3. Emergency service restart
ansible all -i inventories/dynamic.py -a "systemctl restart docker"
./scripts/deploy-dynamic.sh all --tags restart

# 4. Check logs for errors
ansible discord_services -i inventories/dynamic.py \
  -a "docker compose logs --tail=50"

# 5. Manual service restart if needed
ansible atl_wiki_servers -i inventories/dynamic.py \
  -a "docker compose restart mediawiki"
```

#### Security Incident Response

```bash
# 1. Apply immediate security hardening
./scripts/deploy-dynamic.sh all --tags security

# 2. Check for unauthorized access
ansible all -i inventories/dynamic.py -a "last -20"

# 3. Check running processes
ansible all -i inventories/dynamic.py -a "ps aux | head -20"

# 4. Update all passwords/keys immediately
./scripts/deploy-dynamic.sh all --tags users

# 5. Review firewall rules
ansible all -i inventories/dynamic.py -a "iptables -L"
```

#### Infrastructure Failure Recovery

```bash
# 1. Check infrastructure status
cd terraform && terraform show

# 2. Rebuild infrastructure if needed
./scripts/deploy-dynamic.sh infrastructure apply

# 3. Restore configuration
./scripts/deploy-dynamic.sh all

# 4. Restore data from latest backup
ansible backup_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/restore.sh latest"

# 5. Verify all services
ansible all -i inventories/dynamic.py -m ping
```

## 🔧 Maintenance Operations

### Weekly Maintenance

```bash
# Update system packages
ansible all -i inventories/dynamic.py -a "apt update && apt upgrade -y"

# Clean Docker images
ansible all -i inventories/dynamic.py -a "docker system prune -f"

# Check disk usage
ansible all -i inventories/dynamic.py -a "du -sh /opt/* /var/log/*"

# Rotate logs
ansible all -i inventories/dynamic.py -a "logrotate -f /etc/logrotate.conf"
```

### Monthly Maintenance

```bash
# Full system update
./scripts/deploy-dynamic.sh all --tags system

# Security audit
./scripts/lint.sh --security

# Backup verification
ansible backup_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/verify-backups.sh"

# Performance review
ansible all -i inventories/dynamic.py -a "iotop -a -o -d 10 -n 3"
```

## 📊 Monitoring Deployment

### Deployment Logs

```bash
# View deployment progress
tail -f logs/deploy-$(date +%Y%m%d).log

# Check Ansible logs
tail -f ~/.ansible.log

# Check Terraform logs
export TF_LOG=INFO
./scripts/deploy-dynamic.sh infrastructure apply
```

### Health Checks

```bash
# Check all services
./scripts/deploy-dynamic.sh all --tags health_check

# Verify DNS resolution
dig @8.8.8.8 atl.wiki allthingslinux.org

# Check SSL certificates
openssl s_client -connect atl.wiki:443 -servername atl.wiki
```

### Performance Monitoring

```bash
# Check system resources
ansible all -i inventories/dynamic.py -a "df -h && free -m"

# Monitor deployment time
time ./scripts/deploy-dynamic.sh domain atl_tools

# Check database connections
ansible database_servers -i inventories/dynamic.py \
  -a "systemctl status postgresql"
```

## 🎯 Best Practices

### Development Workflow

1. Always test locally with development environment
2. Run linting before every deployment
3. Use dry-run to preview changes
4. Deploy to staging before production
5. Monitor logs during deployment

### Production Safety

1. Plan first - Always run `plan` before `apply`
2. Backup data before major changes
3. Deploy during maintenance windows
4. Have rollback plan ready
5. Monitor after deployment

### Performance Optimization

1. Use tags to deploy only necessary components
2. Limit parallelism for large deployments
3. Use local caching for repeated deployments
4. Monitor resource usage during deployment

## 🚨 Troubleshooting

### Common Deployment Issues

#### "No inventory found"

```bash
# Check if dynamic inventory is executable
chmod +x inventories/dynamic.py

# Test inventory generation
./inventories/dynamic.py --list

# Verify environment variables
echo $HCLOUD_TOKEN $CLOUDFLARE_API_TOKEN
```

#### "SSH connection failed"

```bash
# Check SSH key
ssh-add -l
ssh-add ~/.ssh/atl_infrastructure

# Test direct connection
ssh root@server-ip

# Debug SSH
ssh -vvv root@server-ip
```

#### "Terraform state locked"

```bash
# Check lock info
cd terraform
terraform show

# Force unlock (use carefully)
terraform force-unlock LOCK_ID
```

#### "Domain not found in configuration"

```bash
# Check domains.yml syntax
yamllint domains.yml

# Verify domain is enabled
./scripts/deploy-dynamic.sh config | grep domain_name
```

#### "Ansible task failures"

```bash
# Run with increased verbosity
./scripts/deploy-dynamic.sh domain atl_tools -vvv

# Check specific task
ansible-playbook playbooks/dynamic-deploy.yml \
  --start-at-task "Task Name"

# Skip failing tasks temporarily
./scripts/deploy-dynamic.sh all --skip-tags problematic_tag
```

## 📝 Next Steps

After successful deployment:

1. **[Infrastructure Management](infrastructure.md)** - Learn ongoing management
2. **[Security Operations](security.md)** - Implement security practices
3. **[Development Workflow](development.md)** - Contribute to the infrastructure

## 📚 Additional Resources

- [Terraform Documentation](https://terraform.io/docs)
- [Ansible Documentation](https://docs.ansible.com/)
- [Hetzner Cloud API](https://docs.hetzner.cloud/)
- [Cloudflare API](https://developers.cloudflare.com/api/)
