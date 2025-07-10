# network

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
| [hcloud_network.main](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/network) | resource |
| [hcloud_network_subnet.subnets](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/network_subnet) | resource |
| [hcloud_ssh_key.default](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/ssh_key) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name (production, staging, development) | `string` | n/a | yes |
| <a name="input_ip_range"></a> [ip\_range](#input\_ip\_range) | IP range for the private network | `string` | `"10.0.0.0/16"` | no |
| <a name="input_name"></a> [name](#input\_name) | Name prefix for network resources | `string` | n/a | yes |
| <a name="input_network_zone"></a> [network\_zone](#input\_network\_zone) | Hetzner network zone | `string` | `"eu-central"` | no |
| <a name="input_subnets"></a> [subnets](#input\_subnets) | Map of subnets to create | <pre>map(object({<br>    ip_range = string<br>    zone     = string<br>  }))</pre> | <pre>{<br>  "app": {<br>    "ip_range": "10.0.2.0/24",<br>    "zone": "eu-central-1"<br>  },<br>  "data": {<br>    "ip_range": "10.0.3.0/24",<br>    "zone": "eu-central-1"<br>  },<br>  "web": {<br>    "ip_range": "10.0.1.0/24",<br>    "zone": "eu-central-1"<br>  }<br>}</pre> | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to all resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_network_id"></a> [network\_id](#output\_network\_id) | ID of the created network |
| <a name="output_network_ip_range"></a> [network\_ip\_range](#output\_network\_ip\_range) | IP range of the created network |
| <a name="output_network_name"></a> [network\_name](#output\_network\_name) | Name of the created network |
| <a name="output_ssh_key_id"></a> [ssh\_key\_id](#output\_ssh\_key\_id) | ID of the SSH key |
| <a name="output_ssh_key_name"></a> [ssh\_key\_name](#output\_ssh\_key\_name) | Name of the SSH key |
| <a name="output_subnet_ids"></a> [subnet\_ids](#output\_subnet\_ids) | Map of subnet names to their IDs |
| <a name="output_subnet_ip_ranges"></a> [subnet\_ip\_ranges](#output\_subnet\_ip\_ranges) | Map of subnet names to their IP ranges |
<!-- END_TF_DOCS -->
