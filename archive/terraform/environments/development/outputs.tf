output "network_info" {
  description = "Network information"
  value = {
    network_id   = module.network.network_id
    network_name = module.network.network_name
    ip_range     = module.network.network_ip_range
    subnet_ids   = module.network.subnet_ids
  }
}

output "server_info" {
  description = "Server information"
  value       = module.compute.server_info
  sensitive   = false
}

output "server_public_ips" {
  description = "Public IP addresses of servers"
  value       = module.compute.server_public_ips
}

output "server_private_ips" {
  description = "Private IP addresses of servers"
  value       = module.compute.server_private_ips
}

output "security_info" {
  description = "Security group information"
  value = {
    ssh_firewall_id = module.security.ssh_firewall_id
    web_firewall_id = module.security.web_firewall_id
    firewall_ids    = module.security.firewall_ids
  }
}

output "ssh_connection_info" {
  description = "SSH connection information for servers"
  value = {
    for name, ip in module.compute.server_public_ips :
    name => "ssh -i ~/.ssh/id_rsa root@${ip}"
  }
}

output "environment_summary" {
  description = "Summary of development environment"
  value = {
    environment     = "development"
    server_count    = length(module.compute.server_ids)
    network_range   = module.network.network_ip_range
    firewall_count  = length(module.security.firewall_ids)
    backups_enabled = var.enable_backups
  }
}
