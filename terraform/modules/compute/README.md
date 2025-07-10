# compute

<!-- BEGIN_TF_DOCS -->

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_hcloud"></a> [hcloud](#requirement\_hcloud) | ~> 1.45 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_hcloud"></a> [hcloud](#provider\_hcloud) | 1.51.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [hcloud_server.servers](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server) | resource |
| [hcloud_server_network.server_networks](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server_network) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable_backups"></a> [enable\_backups](#input\_enable\_backups) | Enable backups for servers | `bool` | `true` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (production, staging, development) | `string` | n/a | yes |
| <a name="input_image"></a> [image](#input\_image) | Server image to use | `string` | `"ubuntu-24.04"` | no |
| <a name="input_location"></a> [location](#input\_location) | Server location | `string` | `"nbg1"` | no |
| <a name="input_name"></a> [name](#input\_name) | Name prefix for compute resources | `string` | n/a | yes |
| <a name="input_network_id"></a> [network\_id](#input\_network\_id) | ID of the network to attach servers to | `string` | n/a | yes |
| <a name="input_server_type"></a> [server\_type](#input\_server\_type) | Type of server to create | `string` | `"cx11"` | no |
| <a name="input_servers"></a> [servers](#input\_servers) | Map of servers to create | <pre>map(object({<br>    server_type = optional(string)<br>    location    = optional(string)<br>    image       = optional(string)<br>    labels      = optional(map(string), {})<br>  }))</pre> | `{}` | no |
| <a name="input_ssh_key_ids"></a> [ssh\_key\_ids](#input\_ssh\_key\_ids) | List of SSH key IDs to attach to servers | `list(string)` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_server_ids"></a> [server\_ids](#output\_server\_ids) | Map of server names to their IDs |
| <a name="output_server_info"></a> [server\_info](#output\_server\_info) | Complete server information |
| <a name="output_server_names"></a> [server\_names](#output\_server\_names) | Map of server names to their full names |
| <a name="output_server_private_ips"></a> [server\_private\_ips](#output\_server\_private\_ips) | Map of server names to their private IP addresses |
| <a name="output_server_public_ips"></a> [server\_public\_ips](#output\_server\_public\_ips) | Map of server names to their public IP addresses |
<!-- END_TF_DOCS -->
