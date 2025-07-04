"""Configuration utilities for infrastructure scripts"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from rich.console import Console

from .logging import InfraLogger


class ConfigManager:
    """Manage configuration files and environment"""

    def __init__(self, project_root: Path, logger: InfraLogger):
        self.project_root = project_root
        self.logger = logger
        self.console = Console()

        self.domains_file = project_root / "domains.yml"
        self._domains_config = None

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.logger.info("Checking prerequisites...")

        # Check required files
        if not self.domains_file.exists():
            self.logger.error(f"domains.yml not found at {self.domains_file}")
            return False

        # Check Poetry environment
        if not os.getenv("POETRY_ACTIVE"):
            self.logger.error("Not running in Poetry environment")
            return False

        # Check ansible-playbook
        if not self._command_exists("ansible-playbook"):
            self.logger.error("ansible-playbook not found in PATH")
            return False

        self.logger.success("Prerequisites check passed")
        return True

    def check_environment_variables(
        self, action: str, terraform_only: bool = False
    ) -> bool:
        """Check required environment variables"""
        if action == "apply" and not terraform_only:
            missing_vars = []

            if not os.getenv("HCLOUD_TOKEN"):
                missing_vars.append("HCLOUD_TOKEN")

            if not os.getenv("CLOUDFLARE_API_TOKEN"):
                missing_vars.append("CLOUDFLARE_API_TOKEN")

            if missing_vars:
                self.logger.error(
                    f"Missing required environment variables: {', '.join(missing_vars)}"
                )
                return False

        return True

    def load_domains_config(self) -> Dict:
        """Load domains configuration from YAML file"""
        if self._domains_config is None:
            try:
                with open(self.domains_file, "r") as f:
                    self._domains_config = yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"Failed to load domains config: {e}")
                raise

        return self._domains_config

    def get_enabled_domains(self) -> List[str]:
        """Get list of enabled domains"""
        config = self.load_domains_config()
        enabled_domains = []

        for domain_key, domain_config in config.get("domains", {}).items():
            if domain_config.get("enabled", False) and not domain_config.get(
                "external", False
            ):
                enabled_domains.append(domain_key)

        return enabled_domains

    def get_domain_info(self, domain_key: str) -> Optional[Dict]:
        """Get information about a specific domain"""
        config = self.load_domains_config()
        return config.get("domains", {}).get(domain_key)

    def toggle_domain(self, domain_name: str, enable: bool) -> bool:
        """Enable or disable a domain"""
        config = self.load_domains_config()

        if domain_name not in config.get("domains", {}):
            self.logger.error(f"Domain {domain_name} not found in configuration")
            return False

        # Update configuration
        config["domains"][domain_name]["enabled"] = enable

        # Write back to file
        try:
            with open(self.domains_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            action = "enabled" if enable else "disabled"
            self.logger.success(f"Domain {domain_name} {action} successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update domains config: {e}")
            return False

    def show_config(self):
        """Display current domain configuration"""
        config = self.load_domains_config()

        self.logger.table_start("📋 ENABLED DOMAINS:")
        for domain_key in self.get_enabled_domains():
            domain_info = config["domains"][domain_key]
            domain_name = domain_info.get("domain", "")
            services = domain_info.get("services", [])
            services_str = ",".join(services) if services else "none"

            self.logger.table_row(
                domain_key, f"{domain_name} [{services_str}]", "enabled"
            )

        self.logger.table_start("📋 DISABLED DOMAINS:")
        for domain_key, domain_info in config.get("domains", {}).items():
            if not domain_info.get("enabled", False) or domain_info.get(
                "external", False
            ):
                domain_name = domain_info.get("domain", "")
                reason = (
                    "external" if domain_info.get("external", False) else "disabled"
                )
                self.logger.table_row(domain_key, domain_name, reason)

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run(["which", command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
