#!/usr/bin/env python3
"""
Update Ansible collections using uv
Python version of the bash update-collections.sh script
"""

import os
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from ..common.logging import InfraLogger


class CollectionManager:
    """Manage Ansible collections"""

    def __init__(self, project_root: Path, logger: InfraLogger):
        self.project_root = project_root
        self.logger = logger
        self.console = Console()
        self.requirements_file = project_root / "collections" / "requirements.yml"

    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        self.logger.info("Checking prerequisites...")

        # Check uv environment
        if not os.getenv("VIRTUAL_ENV"):
            self.logger.error("Not running in uv virtual environment")
            return False

        # Check collections requirements file
        if not self.requirements_file.exists():
            self.logger.error(
                f"Collections requirements file not found: {self.requirements_file}"
            )
            return False

        # Check ansible-galaxy
        if not self._command_exists("ansible-galaxy"):
            self.logger.error("ansible-galaxy not found in PATH")
            return False

        self.logger.success("Prerequisites check passed")
        return True

    def update_collections(self, upgrade: bool = True) -> bool:
        """Update Ansible collections"""
        self.logger.info("Installing/updating Ansible collections...")

        try:
            # Build command
            cmd = [
                "ansible-galaxy",
                "collection",
                "install",
                "-r",
                str(self.requirements_file),
            ]

            if upgrade:
                cmd.append("--upgrade")

            # Run the command
            subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=self.project_root
            )

            self.logger.success("Ansible collections updated successfully!")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update Ansible collections: {e}")
            if e.stdout:
                self.logger.debug(f"stdout: {e.stdout}")
            if e.stderr:
                self.logger.debug(f"stderr: {e.stderr}")
            return False

    def list_collections(self) -> list[str]:
        """List installed collections"""
        self.logger.info("Currently installed collections:")

        try:
            result = subprocess.run(
                ["ansible-galaxy", "collection", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Filter for common collections
            collections = []
            for line in result.stdout.split("\n"):
                if any(
                    keyword in line.lower()
                    for keyword in ["hetzner", "community", "ansible"]
                ):
                    collections.append(line.strip())
                    self.logger.info(f"  {line.strip()}")

            return collections

        except subprocess.CalledProcessError as e:
            self.logger.warn(f"Could not list collections: {e}")
            return []

    def show_collection_paths(self):
        """Show where collections are installed"""
        self.logger.info("Collection installation paths:")

        try:
            # Try using ansible-galaxy to get paths
            result = subprocess.run(
                ["ansible-galaxy", "collection", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )

            import json

            data = json.loads(result.stdout)
            if data:
                for path in data.keys():
                    if Path(path).exists():
                        self.logger.info(f"  {path}")
            else:
                self.logger.warn("No collection paths found")

        except subprocess.CalledProcessError:
            self.logger.warn("Could not get collection paths from ansible-galaxy")
        except Exception as e:
            self.logger.warn(f"Could not determine collection paths: {e}")

            # Fallback: try to find common collection paths
            common_paths = [
                Path.home() / ".ansible" / "collections",
                Path("/usr/share/ansible/collections"),
                Path("/usr/local/share/ansible/collections"),
            ]

            found_paths = [p for p in common_paths if p.exists()]
            if found_paths:
                self.logger.info("Found common collection paths:")
                for path in found_paths:
                    self.logger.info(f"  {path}")
            else:
                self.logger.warn("Unable to determine collection paths")

    def verify_hetzner_collection(self) -> bool:
        """Verify that Hetzner Cloud collection is working"""
        self.logger.info("Verifying Hetzner Cloud collection...")

        try:
            subprocess.run(
                ["ansible-doc", "hetzner.hcloud.hcloud_server"],
                check=True,
                capture_output=True,
            )

            self.logger.success("Hetzner Cloud collection is working correctly")
            return True

        except subprocess.CalledProcessError:
            self.logger.warn(
                "Could not verify Hetzner Cloud collection - this may be normal if not configured yet"
            )
            return False

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run(["which", command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


@click.command()
@click.option("--no-upgrade", is_flag=True, help="Skip upgrading existing collections")
@click.option("--verify", is_flag=True, help="Verify collections after update")
def cli(no_upgrade, verify):
    """Update Ansible collections using uv

    This script ensures collections are updated in the correct uv environment
    """
    # Initialize
    project_root = Path(__file__).parent.parent
    logger = InfraLogger("update-collections", project_root / "logs")

    # Show banner
    logger.banner(
        "All Things Linux Collection Update",
        "Updating Ansible collections in uv environment",
    )

    # Initialize collection manager
    collection_manager = CollectionManager(project_root, logger)

    # Check prerequisites
    if not collection_manager.check_prerequisites():
        sys.exit(1)

    # Update collections
    if not collection_manager.update_collections(upgrade=not no_upgrade):
        sys.exit(1)

    # List collections
    collection_manager.list_collections()

    # Show collection paths
    collection_manager.show_collection_paths()

    # Verify Hetzner collection if requested
    if verify:
        collection_manager.verify_hetzner_collection()

    logger.success("Collection update complete!")


if __name__ == "__main__":
    cli()
