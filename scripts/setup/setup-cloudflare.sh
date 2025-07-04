#!/bin/bash

# Cloudflare Setup Script for All Things Linux Infrastructure
# This script helps set up and test Cloudflare API integration

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "=================================================="
echo "   Cloudflare Setup for All Things Linux"
echo "=================================================="
echo -e "${NC}"
echo

# Check if required tools are available
check_dependencies() {
    log "Checking dependencies..."

    local missing_tools=()

    if ! command -v curl &>/dev/null; then
        missing_tools+=("curl")
    fi

    if ! command -v jq &>/dev/null; then
        missing_tools+=("jq")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
        echo "Please install them and run this script again."
        echo
        echo "On Ubuntu/Debian: sudo apt install curl jq"
        echo "On RHEL/CentOS: sudo yum install curl jq"
        echo "On macOS: brew install curl jq"
        exit 1
    fi

    success "All dependencies found"
}

# Guide user through token creation
guide_token_creation() {
    echo -e "${YELLOW}📝 Cloudflare API Token Setup Guide${NC}"
    echo
    echo "You need to create a Cloudflare API token with specific permissions."
    echo
    echo "1. Go to: https://dash.cloudflare.com/profile/api-tokens"
    echo "2. Click 'Create Token'"
    echo "3. Select 'Custom token'"
    echo "4. Configure these permissions:"
    echo "   - Zone: Zone:Read (All zones)"
    echo "   - Zone: Zone Settings:Edit (Include: Zone - your-domain.com)"
    echo "   - DNS: DNS:Edit (Include: Zone - your-domain.com)"
    echo "5. Add zone resource: Include - Zone - your-domain.com"
    echo "6. Copy the token (you won't see it again!)"
    echo
    read -p "Press Enter when you have created your token..."
}

# Get token from user
get_api_token() {
    echo
    log "Enter your Cloudflare API token:"
    echo "(Input will be hidden for security)"
    read -s -p "Token: " CLOUDFLARE_API_TOKEN
    echo

    if [[ -z $CLOUDFLARE_API_TOKEN ]]; then
        error "Token cannot be empty"
        exit 1
    fi

    # Export for testing
    export CLOUDFLARE_API_TOKEN
}

# Test token validity
test_token() {
    log "Testing Cloudflare API token..."

    local response
    response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json")

    if echo "$response" | jq -e '.success' >/dev/null; then
        success "Token is valid!"

        # Show token details
        local token_status
        token_status=$(echo "$response" | jq -r '.result.status')
        echo "  Status: $token_status"

        if echo "$response" | jq -e '.result.not_before' >/dev/null; then
            local not_before
            not_before=$(echo "$response" | jq -r '.result.not_before')
            echo "  Valid from: $not_before"
        fi

        if echo "$response" | jq -e '.result.expires_on' >/dev/null; then
            local expires_on
            expires_on=$(echo "$response" | jq -r '.result.expires_on')
            echo "  Expires: $expires_on"
        fi
    else
        error "Token validation failed!"
        echo "Response: $response"
        return 1
    fi
}

# Get domain from user
get_domain() {
    echo
    log "Enter your domain name (e.g., allthingslinux.org):"
    read -p "Domain: " DOMAIN_NAME

    if [[ -z $DOMAIN_NAME ]]; then
        error "Domain cannot be empty"
        exit 1
    fi

    # Basic domain validation
    if [[ ! $DOMAIN_NAME =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$ ]]; then
        error "Invalid domain format"
        exit 1
    fi
}

# Test domain access
test_domain_access() {
    log "Testing access to domain: $DOMAIN_NAME"

    local response
    response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN_NAME" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json")

    if echo "$response" | jq -e '.success' >/dev/null; then
        local zone_count
        zone_count=$(echo "$response" | jq '.result | length')

        if [[ $zone_count -eq 0 ]]; then
            error "Domain '$DOMAIN_NAME' not found in your Cloudflare account"
            echo
            echo "Make sure:"
            echo "1. The domain is added to your Cloudflare account"
            echo "2. The domain name is spelled correctly"
            echo "3. Your API token has access to this zone"
            return 1
        else
            success "Domain found in Cloudflare!"

            local zone_id
            zone_id=$(echo "$response" | jq -r '.result[0].id')
            local zone_status
            zone_status=$(echo "$response" | jq -r '.result[0].status')

            echo "  Zone ID: $zone_id"
            echo "  Status: $zone_status"

            if [[ $zone_status != "active" ]]; then
                warn "Domain status is '$zone_status' (not active)"
                echo "This might cause issues. Ensure nameservers are properly configured."
            fi
        fi
    else
        error "Failed to check domain access!"
        echo "Response: $response"
        return 1
    fi
}

# Test DNS permissions
test_dns_permissions() {
    log "Testing DNS edit permissions..."

    # Try to list DNS records (read permission test)
    local response
    response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN_NAME" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN")

    if echo "$response" | jq -e '.success' >/dev/null; then
        local zone_id
        zone_id=$(echo "$response" | jq -r '.result[0].id')

        # Test listing DNS records
        local dns_response
        dns_response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?per_page=1" \
            -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN")

        if echo "$dns_response" | jq -e '.success' >/dev/null; then
            success "DNS read permissions verified"

            local record_count
            record_count=$(echo "$dns_response" | jq '.result_info.total_count')
            echo "  Found $record_count DNS records"
        else
            error "DNS read permission test failed!"
            echo "Response: $dns_response"
            return 1
        fi
    else
        error "Could not get zone information for DNS test"
        return 1
    fi
}

# Generate environment file
generate_env_file() {
    local env_file=".env.cloudflare"

    log "Generating environment file: $env_file"

    cat >"$env_file" <<EOF
# Cloudflare API Configuration
# Generated on $(date)

# Cloudflare API Token
export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN"

# Domain Configuration
export DOMAIN_NAME="$DOMAIN_NAME"

# Usage:
# source $env_file
# ./scripts/terraform-deploy.sh -e development -a plan
EOF

    chmod 600 "$env_file"
    success "Environment file created: $env_file"
    echo
    echo "To use this configuration:"
    echo "  source $env_file"
    echo "  ./scripts/terraform-deploy.sh -e development -a plan"
    echo
    warn "Keep this file secure and don't commit it to version control!"
}

# Update terraform.tfvars files
update_terraform_configs() {
    log "Updating Terraform configuration files..."

    local environments=("development" "staging" "production")

    for env in "${environments[@]}"; do
        local tfvars_file="terraform/environments/$env/terraform.tfvars"

        if [[ -f $tfvars_file ]]; then
            # Check if domain_name is already set
            if grep -q "^domain_name" "$tfvars_file"; then
                # Update existing line
                sed -i.bak "s/^domain_name = .*/domain_name = \"$DOMAIN_NAME\"/" "$tfvars_file"
            else
                # Add new line
                echo "domain_name = \"$DOMAIN_NAME\"" >>"$tfvars_file"
            fi
            success "Updated $tfvars_file"
        else
            warn "Terraform config not found: $tfvars_file"
        fi
    done
}

# Main execution
main() {
    check_dependencies

    echo "This script will help you set up Cloudflare integration."
    echo

    # Check if token is already in environment
    if [[ -n ${CLOUDFLARE_API_TOKEN:-} ]]; then
        log "Found existing CLOUDFLARE_API_TOKEN in environment"
        if test_token; then
            success "Existing token is valid"
        else
            warn "Existing token is invalid, please create a new one"
            guide_token_creation
            get_api_token
            test_token
        fi
    else
        guide_token_creation
        get_api_token
        test_token
    fi

    get_domain
    test_domain_access
    test_dns_permissions

    echo
    success "All tests passed! Cloudflare integration is ready."
    echo

    # Ask user what they want to do
    echo "What would you like to do next?"
    echo "1) Generate environment file (.env.cloudflare)"
    echo "2) Update Terraform configurations with domain"
    echo "3) Both"
    echo "4) Nothing (exit)"
    echo
    read -p "Choice (1-4): " choice

    case "$choice" in
    1)
        generate_env_file
        ;;
    2)
        update_terraform_configs
        ;;
    3)
        generate_env_file
        update_terraform_configs
        ;;
    4)
        log "Setup complete. Remember to set CLOUDFLARE_API_TOKEN in your environment."
        ;;
    *)
        warn "Invalid choice. Setup complete."
        ;;
    esac

    echo
    success "Cloudflare setup completed!"
    echo
    echo "Next steps:"
    echo '1. Export your tokens: export HCLOUD_TOKEN="your-hetzner-token"'
    echo "2. Source the environment: source .env.cloudflare"
    echo "3. Deploy infrastructure: ./scripts/terraform-deploy.sh -e development -a apply"
    echo
    echo "For more information, see: docs/CLOUDFLARE_INTEGRATION.md"
}

# Run main function
main "$@"
