# All Things Linux Terraform Infrastructure

This directory contains the Terraform configuration for managing All Things Linux infrastructure, including server provisioning with Hetzner Cloud and DNS/CDN management with Cloudflare.

## Overview

This Terraform configuration provides:

- **Hetzner Cloud Server Provisioning**: Automated server creation with proper sizing and placement
- **Cloudflare DNS Management**: Automated DNS record creation and management
- **Cloudflare CDN Configuration**: Performance optimization and security settings
- **Multi-Environment Support**: Separate configurations for staging and production
- **Integration with Ansible**: Outputs used by Ansible for configuration management

## Usage

### Prerequisites

- Terraform >= 1.0
- Hetzner Cloud API token
- Cloudflare API token
- Environment-specific `.tfvars` files

### Deployment

```bash
# Initialize Terraform
terraform init

# Plan deployment for specific environment
terraform plan -var-file="environments/staging/terraform.tfvars"

# Apply changes
terraform apply -var-file="environments/staging/terraform.tfvars"

# Use automated deployment script (recommended)
../scripts/terraform-deploy.sh -e staging
```

### Environment Management

- **Staging**: `environments/staging/terraform.tfvars`
- **Production**: `environments/production/terraform.tfvars`

Note: Server configurations are now defined in `../domains.yml` which provides a single source of truth for all infrastructure.

## Architecture

### Server Configuration

Servers are provisioned using Hetzner Cloud with:

- Appropriate instance types for each environment
- Cloud-init for initial configuration
- SSH key management
- Network and firewall configuration

### DNS and CDN

Cloudflare provides:

- DNS record management for all services
- SSL/TLS termination and optimization
- Caching and performance optimization
- Security features (DDoS protection, WAF)

## Files

- `main.tf`: Provider configuration and shared resources
- `variables.tf`: Variable definitions and descriptions
- `outputs.tf`: Output values for Ansible integration
- `domains.tf`: Dynamic infrastructure from domains.yml
- `load_balancer.tf`: Load balancer configuration

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_cloudflare"></a> [cloudflare](#requirement\_cloudflare) | ~> 5.6 |
| <a name="requirement_hcloud"></a> [hcloud](#requirement\_hcloud) | ~> 1.45 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_cloudflare"></a> [cloudflare](#provider\_cloudflare) | 5.6.0 |
| <a name="provider_hcloud"></a> [hcloud](#provider\_hcloud) | 1.51.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [cloudflare_dns_record.domain_main](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/dns_record) | resource |
| [cloudflare_dns_record.domain_subdomains](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/dns_record) | resource |
| [cloudflare_origin_ca_certificate.main](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/origin_ca_certificate) | resource |
| [cloudflare_page_rule.api_cache](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/page_rule) | resource |
| [cloudflare_zone.domains](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/zone) | resource |
| [hcloud_firewall.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/firewall) | resource |
| [hcloud_load_balancer.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/load_balancer) | resource |
| [hcloud_load_balancer_network.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/load_balancer_network) | resource |
| [hcloud_load_balancer_service.http](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/load_balancer_service) | resource |
| [hcloud_load_balancer_service.https](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/load_balancer_service) | resource |
| [hcloud_load_balancer_target.web_servers](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/load_balancer_target) | resource |
| [hcloud_network.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/network) | resource |
| [hcloud_network_subnet.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/network_subnet) | resource |
| [hcloud_server.domains](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server) | resource |
| [hcloud_server.shared](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server) | resource |
| [hcloud_ssh_key.default](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/ssh_key) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_ssh_ips"></a> [allowed\_ssh\_ips](#input\_allowed\_ssh\_ips) | List of IP addresses allowed to SSH | `list(string)` | <pre>[<br>  "0.0.0.0/0"<br>]</pre> | no |
| <a name="input_cloudflare_account_id"></a> [cloudflare\_account\_id](#input\_cloudflare\_account\_id) | Cloudflare account ID | `string` | n/a | yes |
| <a name="input_cloudflare_api_token"></a> [cloudflare\_api\_token](#input\_cloudflare\_api\_token) | Cloudflare API token | `string` | n/a | yes |
| <a name="input_csr_content"></a> [csr\_content](#input\_csr\_content) | CSR content for Origin CA certificate | `string` | `""` | no |
| <a name="input_dns_ttl"></a> [dns\_ttl](#input\_dns\_ttl) | DNS TTL for records | `number` | `300` | no |
| <a name="input_enable_api_caching"></a> [enable\_api\_caching](#input\_enable\_api\_caching) | Enable API endpoint caching | `bool` | `false` | no |
| <a name="input_enable_origin_ca"></a> [enable\_origin\_ca](#input\_enable\_origin\_ca) | Enable Cloudflare Origin CA certificate | `bool` | `false` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (development, staging, production) | `string` | n/a | yes |
| <a name="input_hcloud_token"></a> [hcloud\_token](#input\_hcloud\_token) | Hetzner Cloud API token | `string` | n/a | yes |
| <a name="input_load_balancer_enabled"></a> [load\_balancer\_enabled](#input\_load\_balancer\_enabled) | Whether to create a load balancer | `bool` | `false` | no |
| <a name="input_load_balancer_type"></a> [load\_balancer\_type](#input\_load\_balancer\_type) | Type of load balancer | `string` | `"lb11"` | no |
| <a name="input_network_cidr"></a> [network\_cidr](#input\_network\_cidr) | CIDR block for the main network | `string` | `"10.0.0.0/16"` | no |
| <a name="input_network_zone"></a> [network\_zone](#input\_network\_zone) | Network zone for the subnet | `string` | `"eu-central"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | Name of the project | `string` | `"allthingslinux"` | no |
| <a name="input_public_key_path"></a> [public\_key\_path](#input\_public\_key\_path) | Path to the public SSH key | `string` | `"~/.ssh/id_rsa.pub"` | no |
| <a name="input_server_image"></a> [server\_image](#input\_server\_image) | Server image to use for all servers | `string` | `"ubuntu-24.04"` | no |
| <a name="input_server_locations"></a> [server\_locations](#input\_server\_locations) | List of server locations | `list(string)` | `[]` | no |
| <a name="input_subnet_cidr"></a> [subnet\_cidr](#input\_subnet\_cidr) | CIDR block for the subnet | `string` | `"10.0.1.0/24"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_ansible_inventory"></a> [ansible\_inventory](#output\_ansible\_inventory) | Dynamically generated Ansible inventory from domains.yml |
| <a name="output_cloudflare"></a> [cloudflare](#output\_cloudflare) | Cloudflare configuration information |
| <a name="output_firewall"></a> [firewall](#output\_firewall) | Firewall information |
| <a name="output_load_balancer"></a> [load\_balancer](#output\_load\_balancer) | Load balancer information |
| <a name="output_network"></a> [network](#output\_network) | Network information |
| <a name="output_servers"></a> [servers](#output\_servers) | Server information for Ansible inventory |
| <a name="output_ssh_key"></a> [ssh\_key](#output\_ssh\_key) | SSH key information |
<!-- END_TF_DOCS -->

## Related Documentation

- [Terraform Hetzner Guide](../docs/TERRAFORM_HETZNER_GUIDE.md)
- [Cloudflare Integration](../docs/CLOUDFLARE_INTEGRATION.md)
- [Pre-commit Terraform Integration](../docs/PRE_COMMIT_TERRAFORM.md)
