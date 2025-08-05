# Secrets Management Guide

This guide explains how to properly manage secrets in the All Things Linux infrastructure monorepo.

## 🤔 **The Problem: Duplicate Secrets**

You might notice we have different places that seem to want the same secrets:

- `terraform/environments/*/terraform.tfvars` (Terraform secrets)
- `configs/secrets.yml` (Ansible secrets)

**This is intentional separation, not duplication!** Here's why:

## 🏗️ **Architecture: Separate Tools, Separate Secrets**

### **Terraform Secrets** (Infrastructure Provisioning)

- **Purpose**: Create servers, networks, DNS records
- **Needs**: Cloud provider API tokens (Hetzner, Cloudflare)
- **Best Practice**: Use environment variables

### **Ansible Secrets** (Application Configuration)

- **Purpose**: Configure services, databases, applications
- **Needs**: Database passwords, app secrets, certificates
- **Best Practice**: Use encrypted YAML files

## ✅ **Recommended Approach**

### **1. Terraform: Environment Variables (Preferred)**

```bash
# Set environment variables (most secure)
export TF_VAR_hetzner_token="your_actual_token_here"
export TF_VAR_cloudflare_api_token="your_actual_token_here"

# Now Terraform can access these automatically
cd terraform/environments/development
terraform plan  # Uses environment variables
```

**Benefits:**

- ✅ No secrets in files
- ✅ Works with CI/CD systems
- ✅ Easy to rotate tokens
- ✅ Shell history can be excluded

### **2. Ansible: Encrypted YAML Files**

```bash
# Create and edit Ansible secrets
cp configs/secrets.example.yml configs/secrets.yml
# Edit configs/secrets.yml with actual values

# Optional: Encrypt with ansible-vault
ansible-vault encrypt configs/secrets.yml
```

**Benefits:**

- ✅ Version controlled (encrypted)
- ✅ Role-based access
- ✅ Application-specific secrets
- ✅ Ansible integration

## 🚀 **Quick Setup**

We've created a helper script to set this up properly:

```bash
# Run the automated setup
./scripts/setup/setup-secrets.sh

# This will:
# 1. Create configs/secrets.yml from template
# 2. Set up ~/.config/atl-infra/env for Terraform
# 3. Optionally configure shell integration
# 4. Validate the setup
```

## 📋 **Manual Setup**

### **Step 1: Terraform Environment Variables**

Create `~/.config/atl-infra/env`:

```bash
# All Things Linux Infrastructure Environment Variables
export TF_VAR_hetzner_token="your_hetzner_api_token_here"
export TF_VAR_cloudflare_api_token="your_cloudflare_api_token_here"
export TF_WORKSPACE="development"
```

Source it in your shell:

```bash
# Add to ~/.zshrc or ~/.bashrc
[ -f ~/.config/atl-infra/env ] && source ~/.config/atl-infra/env
```

### **Step 2: Ansible Secrets File**

```bash
# Create from template
cp configs/secrets.example.yml configs/secrets.yml

# Edit with your actual values
vim configs/secrets.yml
```

### **Step 3: Test the Setup**

```bash
# Test Terraform (should work without terraform.tfvars)
cd terraform/environments/development
terraform plan

# Test Ansible (should find secrets.yml)
cd ../../ansible
ansible-playbook --syntax-check playbooks/site.yml
```

## 🔒 **Security Best Practices**

### **Environment Variables**

- ✅ Use environment variables for Terraform
- ✅ Store in `~/.config/atl-infra/env` (not in project)
- ✅ Add to CI/CD system secrets
- ❌ Never put in shell history
- ❌ Never commit environment files

### **Files**

- ✅ Use `configs/secrets.yml` for Ansible only
- ✅ Always gitignore actual secrets files
- ✅ Consider `ansible-vault` encryption
- ❌ Never commit unencrypted secrets

### **Production**

- ✅ Use external secret management (Vault, etc.)
- ✅ Rotate secrets regularly
- ✅ Audit secret access
- ✅ Use service accounts vs personal tokens

## 🏢 **Environment-Specific Patterns**

### **Development**

```bash
# Local environment variables
source ~/.config/atl-infra/env
cd terraform/environments/development
terraform apply
```

### **CI/CD (GitHub Actions)**

```yaml
# .github/workflows/terraform.yml
env:
  TF_VAR_hetzner_token: ${{ secrets.HETZNER_TOKEN }}
  TF_VAR_cloudflare_api_token: ${{ secrets.CLOUDFLARE_TOKEN }}
```

### **Production Environment**

```bash
# External secret management
export TF_VAR_hetzner_token=$(vault kv get -field=token secret/hetzner)
export TF_VAR_cloudflare_api_token=$(vault kv get -field=token secret/cloudflare)
```

## 🔄 **Migration from terraform.tfvars**

If you're currently using `terraform.tfvars` files:

```bash
# 1. Back up current approach
cp terraform/environments/development/terraform.tfvars terraform.tfvars.backup

# 2. Extract secrets to environment
grep "_token" terraform.tfvars.backup >> ~/.config/atl-infra/env
# Edit the env file to use export statements

# 3. Remove secrets from tfvars
grep -v "_token" terraform.tfvars.backup > terraform/environments/development/terraform.tfvars

# 4. Test new approach
source ~/.config/atl-infra/env
terraform plan
```

## 🐛 **Troubleshooting**

### **Terraform can't find variables**

```bash
# Check environment variables are set
env | grep TF_VAR_

# Source environment file
source ~/.config/atl-infra/env

# Verify Terraform sees them
terraform console
> var.hetzner_token
```

### **Ansible can't find secrets**

```bash
# Check secrets file exists
ls -la configs/secrets.yml

# Verify YAML syntax
yamllint configs/secrets.yml

# Test Ansible variable loading
ansible-playbook playbooks/site.yml --list-tasks
```

### **CI/CD issues**

```bash
# Check GitHub secrets are configured
# GitHub → Settings → Secrets and variables → Actions

# Verify workflow environment variables
cat .github/workflows/terraform.yml | grep TF_VAR_
```

## 📚 **Why This Separation?**

| Tool | Purpose | Secrets Type | Storage Method |
|------|---------|--------------|----------------|
| **Terraform** | Infrastructure provisioning | Cloud API tokens | Environment variables |
| **Ansible** | Application configuration | App passwords, certs | Encrypted YAML files |

This separation follows the **principle of least privilege** and **tool-specific best practices**.

## 🎯 **Summary**

- **Terraform**: Use environment variables (`TF_VAR_*`)
- **Ansible**: Use `configs/secrets.yml`
- **Never**: Commit secrets to git
- **Always**: Use the setup script for consistency

```bash
# One command to rule them all
./scripts/setup/setup-secrets.sh
```

This approach is used by professional platform engineering teams and follows industry security standards!
