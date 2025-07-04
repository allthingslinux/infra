#!/usr/bin/env python3
"""
Dynamic Ansible Inventory for All Things Linux Infrastructure
Generates inventory from domains.yml configuration and integrates with Terraform outputs for IP addresses
"""

import json
import sys
import yaml
import argparse
import subprocess
from pathlib import Path


def load_domains_config():
    """Load configuration from domains.yml"""
    script_dir = Path(__file__).parent
    domains_file = script_dir.parent / "domains.yml"

    if not domains_file.exists():
        print(f"ERROR: domains.yml not found at {domains_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(domains_file, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse domains.yml: {e}", file=sys.stderr)
        sys.exit(1)


def load_terraform_inventory():
    """Load Terraform ansible_inventory output if available"""
    script_dir = Path(__file__).parent
    terraform_dir = script_dir.parent / "terraform"

    if not terraform_dir.exists():
        return None

    try:
        # Try to get Terraform output
        result = subprocess.run(
            ["terraform", "output", "-json", "ansible_inventory"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            terraform_output = json.loads(result.stdout)
            # The output is JSON-encoded, so we need to decode it
            return json.loads(terraform_output)
        else:
            print(
                f"DEBUG: Terraform output not available: {result.stderr}",
                file=sys.stderr,
            )
            return None

    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        FileNotFoundError,
    ) as e:
        print(f"DEBUG: Could not load Terraform inventory: {e}", file=sys.stderr)
        return None


def generate_inventory():
    """Generate Ansible inventory from domains.yml and integrate with Terraform outputs"""
    config = load_domains_config()
    terraform_inventory = load_terraform_inventory()

    inventory = {"_meta": {"hostvars": {}}, "all": {"children": []}}

    # Environment (default to production)
    environment = config.get("global", {}).get("environment", "production")
    project_name = config.get("global", {}).get("project_name", "allthingslinux")

    # Process enabled domains
    enabled_domains = {
        name: domain_config
        for name, domain_config in config.get("domains", {}).items()
        if domain_config.get("enabled", False)
        and not domain_config.get("external", False)
    }

    # Process enabled shared infrastructure
    enabled_shared = {
        name: infra_config
        for name, infra_config in config.get("shared_infrastructure", {}).items()
        if infra_config.get("enabled", False)
    }

    # Create domain-based groups
    for domain_key, domain_config in enabled_domains.items():
        server_name = f"{project_name}-{domain_key}-{environment}"

        # Create group for this domain
        inventory[domain_key] = {"hosts": [server_name]}
        inventory["all"]["children"].append(domain_key)

        # Start with base host variables from domains.yml
        host_vars = {
            "ansible_user": config.get("global", {}).get("default_user", "ansible"),
            "server_role": domain_key,
            "domain": domain_config.get("domain"),
            "services": domain_config.get("services", []),
            "deployment_environment": environment,  # Renamed to avoid Ansible reserved word
            "project": project_name,
            "server_type": domain_config.get("server", {}).get("type", "cx31"),
            "location": domain_config.get("server", {}).get("location", "ash"),
            "monitoring_enabled": domain_config.get("monitoring", {}).get(
                "enabled", True
            ),
            "backup_enabled": config.get("global", {}).get("backup_enabled", True),
            # Add subdomains if they exist
            "subdomains": domain_config.get("subdomains", []),
            # Add network configuration
            "network_subnet": domain_config.get("network", {}).get(
                "subnet", "172.20.0.0/16"
            ),
            # Add specific features
            **{
                k: v
                for k, v in domain_config.items()
                if k
                not in [
                    "enabled",
                    "domain",
                    "server",
                    "services",
                    "monitoring",
                    "network",
                    "subdomains",
                ]
            },
        }

        # Override with Terraform inventory data if available (especially ansible_host)
        if terraform_inventory and domain_key in terraform_inventory.get("all", {}).get(
            "children", {}
        ):
            tf_host_data = (
                terraform_inventory["all"]["children"][domain_key]
                .get("hosts", {})
                .get(server_name, {})
            )
            if tf_host_data:
                # Terraform provides the critical ansible_host (IP address)
                host_vars.update(tf_host_data)
                print(
                    f"DEBUG: Using Terraform IP for {server_name}: {tf_host_data.get('ansible_host')}",
                    file=sys.stderr,
                )

        inventory["_meta"]["hostvars"][server_name] = host_vars

    # Create shared infrastructure groups
    for infra_key, infra_config in enabled_shared.items():
        server_name = f"{project_name}-{infra_key}-{environment}"

        # Create group for this shared infrastructure
        inventory[infra_key] = {"hosts": [server_name]}
        inventory["all"]["children"].append(infra_key)

        # Start with base host variables from domains.yml
        host_vars = {
            "ansible_user": config.get("global", {}).get("default_user", "ansible"),
            "server_role": infra_key,
            "services": infra_config.get("services", []),
            "deployment_environment": environment,  # Renamed to avoid Ansible reserved word
            "project": project_name,
            "server_type": infra_config.get("server", {}).get("type", "cx31"),
            "location": infra_config.get("server", {}).get("location", "ash"),
            "shared_infrastructure": True,
            "monitoring_enabled": True,
            "backup_enabled": True,
            # Add domain if specified
            "domain": infra_config.get("domain", f"{infra_key}.{project_name}.local"),
            # Add any additional configuration
            **{
                k: v
                for k, v in infra_config.items()
                if k not in ["enabled", "server", "services", "domain"]
            },
        }

        # Override with Terraform inventory data if available (especially ansible_host)
        if terraform_inventory and infra_key in terraform_inventory.get("all", {}).get(
            "children", {}
        ):
            tf_host_data = (
                terraform_inventory["all"]["children"][infra_key]
                .get("hosts", {})
                .get(server_name, {})
            )
            if tf_host_data:
                # Terraform provides the critical ansible_host (IP address)
                host_vars.update(tf_host_data)
                print(
                    f"DEBUG: Using Terraform IP for {server_name}: {tf_host_data.get('ansible_host')}",
                    file=sys.stderr,
                )

        inventory["_meta"]["hostvars"][server_name] = host_vars

    # Create service-based groups for easier targeting
    service_groups = {}
    for host_name, host_vars in inventory["_meta"]["hostvars"].items():
        for service in host_vars.get("services", []):
            service_group = f"service_{service.replace('-', '_')}"
            if service_group not in service_groups:
                service_groups[service_group] = {"hosts": []}
            service_groups[service_group]["hosts"].append(host_name)

    # Add service groups to inventory
    for group_name, group_data in service_groups.items():
        inventory[group_name] = group_data
        inventory["all"]["children"].append(group_name)

    # Create environment-based groups
    inventory[f"env_{environment}"] = {
        "hosts": list(inventory["_meta"]["hostvars"].keys())
    }
    inventory["all"]["children"].append(f"env_{environment}")

    # Create role-based groups
    role_groups = {}
    for host_name, host_vars in inventory["_meta"]["hostvars"].items():
        role = host_vars.get("server_role", "unknown")
        role_group = f"role_{role}"
        if role_group not in role_groups:
            role_groups[role_group] = {"hosts": []}
        role_groups[role_group]["hosts"].append(host_name)

    # Add role groups to inventory
    for group_name, group_data in role_groups.items():
        inventory[group_name] = group_data
        inventory["all"]["children"].append(group_name)

    return inventory


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Dynamic Ansible Inventory")
    parser.add_argument("--list", action="store_true", help="List all hosts")
    parser.add_argument("--host", help="Get host variables")

    args = parser.parse_args()

    if args.list:
        inventory = generate_inventory()
        print(json.dumps(inventory, indent=2))
    elif args.host:
        # For individual host queries, return the host vars
        inventory = generate_inventory()
        host_vars = inventory.get("_meta", {}).get("hostvars", {}).get(args.host, {})
        print(json.dumps(host_vars, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
