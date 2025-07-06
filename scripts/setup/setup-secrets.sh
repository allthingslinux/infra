#!/bin/bash
# Setup script for infrastructure secrets
# This script helps configure secrets using environment variables (recommended)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." &>/dev/null && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 All Things Linux - Secrets Setup${NC}"
echo "================================================"

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/configs/secrets.example.yml" ]]; then
    echo -e "${RED}❌ Error: Run this script from the project root${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Setting up secrets for infrastructure...${NC}"
echo

# 1. Create Ansible secrets file if it doesn't exist
if [[ ! -f "$PROJECT_ROOT/configs/secrets.yml" ]]; then
    echo -e "${BLUE}📝 Creating Ansible secrets file...${NC}"
    cp "$PROJECT_ROOT/configs/secrets.example.yml" "$PROJECT_ROOT/configs/secrets.yml"
    echo -e "${GREEN}✅ Created configs/secrets.yml${NC}"
    echo -e "${YELLOW}⚠️  Edit configs/secrets.yml with your actual values${NC}"
else
    echo -e "${GREEN}✅ configs/secrets.yml already exists${NC}"
fi

# 2. Set up environment variables for Terraform
echo
echo -e "${BLUE}🌍 Setting up Terraform environment variables...${NC}"

# Check if environment variables are already set
ENV_FILE="$HOME/.config/atl-infra/env"
mkdir -p "$(dirname "$ENV_FILE")"

if [[ ! -f $ENV_FILE ]]; then
    echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
    cat >"$ENV_FILE" <<'EOF'
# All Things Linux Infrastructure Environment Variables
# Source this file to set up your development environment
# Usage: source ~/.config/atl-infra/env

# Terraform Variables (replace with your actual tokens)
export TF_VAR_hetzner_token="your_hetzner_api_token_here"
export TF_VAR_cloudflare_api_token="your_cloudflare_api_token_here"

# Optional: Set default Terraform environment
export TF_WORKSPACE="development"

# Optional: Enable Terraform logging for debugging
# export TF_LOG="DEBUG"

echo "✅ ATL Infrastructure environment loaded"
EOF
    echo -e "${GREEN}✅ Created $ENV_FILE${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists: $ENV_FILE${NC}"
fi

# 3. Set up shell integration
echo
echo -e "${BLUE}🐚 Setting up shell integration...${NC}"

SHELL_RC=""
if [[ -n ${ZSH_VERSION:-} ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -n ${BASH_VERSION:-} ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n $SHELL_RC ]] && [[ -f $SHELL_RC ]]; then
    if ! grep -q "atl-infra/env" "$SHELL_RC"; then
        echo
        echo -e "${YELLOW}Would you like to automatically source the environment file in your shell? (y/N)${NC}"
        read -r response
        if [[ $response =~ ^[Yy]$ ]]; then
            {
                echo ""
                echo "# All Things Linux Infrastructure"
                echo "[ -f ~/.config/atl-infra/env ] && source ~/.config/atl-infra/env"
            } >>"$SHELL_RC"
            echo -e "${GREEN}✅ Added auto-sourcing to $SHELL_RC${NC}"
        fi
    else
        echo -e "${GREEN}✅ Shell integration already configured${NC}"
    fi
fi

# 4. Validate setup
echo
echo -e "${BLUE}🔍 Validating setup...${NC}"

# Check Ansible secrets
if [[ -f "$PROJECT_ROOT/configs/secrets.yml" ]]; then
    if grep -q "your_.*_here" "$PROJECT_ROOT/configs/secrets.yml"; then
        echo -e "${YELLOW}⚠️  Remember to edit configs/secrets.yml with real values${NC}"
    else
        echo -e "${GREEN}✅ Ansible secrets file configured${NC}"
    fi
fi

# Check environment variables
if [[ -f $ENV_FILE ]]; then
    if grep -q "your_.*_here" "$ENV_FILE"; then
        echo -e "${YELLOW}⚠️  Remember to edit $ENV_FILE with real tokens${NC}"
    else
        echo -e "${GREEN}✅ Environment file configured${NC}"
    fi
fi

echo
echo -e "${GREEN}🎉 Secrets setup complete!${NC}"
echo
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Edit $ENV_FILE with your actual API tokens"
echo "2. Edit configs/secrets.yml with your actual passwords"
echo "3. Source the environment: source $ENV_FILE"
echo "4. Test Terraform: cd terraform/environments/development && terraform plan"
echo
echo -e "${YELLOW}💡 Pro tips:${NC}"
echo "• Use environment variables for Terraform (more secure)"
echo "• Use configs/secrets.yml for Ansible (application secrets)"
echo "• Never commit actual secrets to git"
echo "• Consider using ansible-vault for additional encryption"
echo
echo -e "${BLUE}📚 Documentation:${NC}"
echo "• Development Guide: docs/guides/development.md"
echo "• Security Guide: docs/guides/security.md"
