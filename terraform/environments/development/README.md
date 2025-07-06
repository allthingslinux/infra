# development

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_hcloud"></a> [hcloud](#requirement\_hcloud) | ~> 1.45 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_compute"></a> [compute](#module\_compute) | ../../modules/compute | n/a |
| <a name="module_network"></a> [network](#module\_network) | ../../modules/network | n/a |
| <a name="module_security"></a> [security](#module\_security) | ../../modules/security | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable_backups"></a> [enable\_backups](#input\_enable\_backups) | Enable automated backups | `bool` | `false` | no |
| <a name="input_hetzner_token"></a> [hetzner\_token](#input\_hetzner\_token) | Hetzner Cloud API token | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_environment_summary"></a> [environment\_summary](#output\_environment\_summary) | Summary of development environment |
| <a name="output_network_info"></a> [network\_info](#output\_network\_info) | Network information |
| <a name="output_security_info"></a> [security\_info](#output\_security\_info) | Security group information |
| <a name="output_server_info"></a> [server\_info](#output\_server\_info) | Server information |
| <a name="output_server_private_ips"></a> [server\_private\_ips](#output\_server\_private\_ips) | Private IP addresses of servers |
| <a name="output_server_public_ips"></a> [server\_public\_ips](#output\_server\_public\_ips) | Public IP addresses of servers |
| <a name="output_ssh_connection_info"></a> [ssh\_connection\_info](#output\_ssh\_connection\_info) | SSH connection information for servers |
<!-- END_TF_DOCS -->
