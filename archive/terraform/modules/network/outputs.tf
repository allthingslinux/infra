output "network_id" {
  description = "ID of the created network"
  value       = hcloud_network.main.id
}

output "network_name" {
  description = "Name of the created network"
  value       = hcloud_network.main.name
}

output "network_ip_range" {
  description = "IP range of the created network"
  value       = hcloud_network.main.ip_range
}

output "subnet_ids" {
  description = "Map of subnet names to their IDs"
  value = {
    for name, subnet in hcloud_network_subnet.subnets : name => subnet.id
  }
}

output "subnet_ip_ranges" {
  description = "Map of subnet names to their IP ranges"
  value = {
    for name, subnet in hcloud_network_subnet.subnets : name => subnet.ip_range
  }
}

output "ssh_key_id" {
  description = "ID of the SSH key"
  value       = hcloud_ssh_key.default.id
}

output "ssh_key_name" {
  description = "Name of the SSH key"
  value       = hcloud_ssh_key.default.name
}
