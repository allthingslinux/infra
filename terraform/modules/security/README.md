# security

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
| [hcloud_firewall.custom](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/firewall) | resource |
| [hcloud_firewall.ssh](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/firewall) | resource |
| [hcloud_firewall.web](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/firewall) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_ips"></a> [allowed\_ips](#input\_allowed\_ips) | List of IP addresses allowed for SSH access | `list(string)` | <pre>[<br>  "0.0.0.0/0"<br>]</pre> | no |
| <a name="input_custom_rules"></a> [custom\_rules](#input\_custom\_rules) | Custom firewall rules | <pre>list(object({<br>    direction   = string<br>    port        = optional(string)<br>    protocol    = optional(string, "tcp")<br>    source_ips  = optional(list(string), [])<br>    description = optional(string)<br>  }))</pre> | `[]` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (production, staging, development) | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Name prefix for security resources | `string` | n/a | yes |
| <a name="input_ssh_port"></a> [ssh\_port](#input\_ssh\_port) | SSH port to allow | `number` | `22` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | `{}` | no |
| <a name="input_web_ports"></a> [web\_ports](#input\_web\_ports) | List of web ports to allow | `list(number)` | <pre>[<br>  80,<br>  443<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_custom_firewall_id"></a> [custom\_firewall\_id](#output\_custom\_firewall\_id) | ID of the custom firewall (if created) |
| <a name="output_custom_firewall_name"></a> [custom\_firewall\_name](#output\_custom\_firewall\_name) | Name of the custom firewall (if created) |
| <a name="output_firewall_ids"></a> [firewall\_ids](#output\_firewall\_ids) | List of all firewall IDs |
| <a name="output_ssh_firewall_id"></a> [ssh\_firewall\_id](#output\_ssh\_firewall\_id) | ID of the SSH firewall |
| <a name="output_ssh_firewall_name"></a> [ssh\_firewall\_name](#output\_ssh\_firewall\_name) | Name of the SSH firewall |
| <a name="output_web_firewall_id"></a> [web\_firewall\_id](#output\_web\_firewall\_id) | ID of the web firewall |
| <a name="output_web_firewall_name"></a> [web\_firewall\_name](#output\_web\_firewall\_name) | Name of the web firewall |
<!-- END_TF_DOCS -->
