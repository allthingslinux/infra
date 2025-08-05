output "ssh_firewall_id" {
  description = "ID of the SSH firewall"
  value       = hcloud_firewall.ssh.id
}

output "ssh_firewall_name" {
  description = "Name of the SSH firewall"
  value       = hcloud_firewall.ssh.name
}

output "web_firewall_id" {
  description = "ID of the web firewall"
  value       = hcloud_firewall.web.id
}

output "web_firewall_name" {
  description = "Name of the web firewall"
  value       = hcloud_firewall.web.name
}

output "custom_firewall_id" {
  description = "ID of the custom firewall (if created)"
  value       = length(var.custom_rules) > 0 ? hcloud_firewall.custom[0].id : null
}

output "custom_firewall_name" {
  description = "Name of the custom firewall (if created)"
  value       = length(var.custom_rules) > 0 ? hcloud_firewall.custom[0].name : null
}

output "firewall_ids" {
  description = "List of all firewall IDs"
  value = compact([
    hcloud_firewall.ssh.id,
    hcloud_firewall.web.id,
    length(var.custom_rules) > 0 ? hcloud_firewall.custom[0].id : null
  ])
}
