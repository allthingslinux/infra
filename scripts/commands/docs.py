#!/usr/bin/env python3
"""
All Things Linux Infrastructure Documentation Generator

This module provides automated documentation generation for infrastructure,
including Terraform modules, Ansible playbooks, and live infrastructure diagrams.
"""

import click
import subprocess
import os
import sys
import yaml
import json
from pathlib import Path
from typing import Optional, List
import shutil

from ..common.logging import InfraLogger
from ..common.config import ConfigManager


class DocumentationManager:
    """Manages infrastructure documentation generation and automation."""

    def __init__(self, logger: InfraLogger):
        """Initialize the documentation manager."""
        self.logger = logger
        self.config = ConfigManager(Path.cwd(), logger)
        self.docs_dir = Path("docs")
        self.scripts_dir = Path("scripts")

    def check_dependencies(self) -> bool:
        """Check if required tools are installed."""
        self.logger.info("Checking for required tools...")
        required_tools = {
            "terraform-docs": "Required for Terraform documentation.",
            "dot": "Required for infrastructure diagrams (part of graphviz).",
            "mkdocs": "Required to build the documentation site.",
            "terraform": "Required to generate infrastructure diagrams.",
        }

        missing_tools = []
        for tool, reason in required_tools.items():
            if not shutil.which(tool):
                missing_tools.append(f"  - {tool}: {reason}")

        if missing_tools:
            self.logger.error("Missing required tools:")
            for tool_info in missing_tools:
                self.logger.warn(tool_info)
            self.logger.info("Please install missing tools or run with --install-tools")
            return False

        self.logger.success("All required tools are installed.")
        return True

    def install_external_tools(self) -> bool:
        """Install external documentation tools."""
        self.logger.info("Installing external documentation tools...")
        success = True
        success &= self._install_terraform_docs()

        if success:
            self.logger.success("External tools installed successfully.")
        else:
            self.logger.error("Failed to install one or more external tools.")
        return success

    def _install_terraform_docs(self) -> bool:
        """Install terraform-docs binary."""
        if shutil.which("terraform-docs"):
            self.logger.info("terraform-docs is already installed.")
            return True

        self.logger.info("Installing terraform-docs...")
        try:
            if sys.platform == "linux":
                arch = "linux-amd64"
            elif sys.platform == "darwin":
                arch = "darwin-amd64"
            else:
                self.logger.error(f"Unsupported OS: {sys.platform}")
                return False

            version = "v0.17.0"
            url = f"https://terraform-docs.io/dl/{version}/terraform-docs-{version}-{arch}.tar.gz"
            download_path = Path("/tmp/terraform-docs.tar.gz")

            subprocess.run(
                ["curl", "-sSLo", str(download_path), url],
                check=True,
            )
            subprocess.run(
                ["tar", "-xzf", str(download_path), "-C", "/tmp"], check=True
            )
            subprocess.run(
                ["sudo", "mv", "/tmp/terraform-docs", "/usr/local/bin/"], check=True
            )
            subprocess.run(
                ["sudo", "chmod", "+x", "/usr/local/bin/terraform-docs"], check=True
            )
            download_path.unlink()
            self.logger.success("terraform-docs installed successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Failed to install terraform-docs: {e}")
            if isinstance(e, subprocess.CalledProcessError):
                self.logger.error(e.stderr.decode())
            return False

    def generate_terraform_docs(self) -> bool:
        """Generate Terraform module documentation."""
        self.logger.info("Generating Terraform documentation...")

        terraform_dir = Path("terraform")
        if not terraform_dir.exists():
            self.logger.warn("No terraform directory found")
            return True

        modules_processed = 0
        for root, dirs, files in os.walk(terraform_dir):
            # Exclude the .terraform directory from the walk
            if ".terraform" in dirs:
                dirs.remove(".terraform")

            root_path = Path(root)
            if any(f.endswith(".tf") for f in files):
                self.logger.info(f"Processing Terraform module: {root_path}")
                try:
                    subprocess.run(
                        [
                            "terraform-docs",
                            "markdown",
                            "table",
                            "--output-file",
                            "README.md",
                            "--output-mode",
                            "inject",
                            str(root_path),
                        ],
                        check=True,
                        capture_output=True,
                    )
                    modules_processed += 1
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to generate docs for {root_path}: {e}")
                    return False

        if modules_processed > 0:
            self._generate_terraform_index(terraform_dir)
            self.logger.success(
                f"Generated Terraform documentation for {modules_processed} modules"
            )
        else:
            self.logger.warn("No Terraform modules found to document")

        return True

    def _generate_terraform_index(self, terraform_dir: Path):
        """Generate a Terraform module index page for MkDocs."""
        self.logger.info("Generating Terraform module index...")
        infrastructure_dir = self.docs_dir / "infrastructure"
        infrastructure_dir.mkdir(parents=True, exist_ok=True)
        tf_doc_path = infrastructure_dir / "terraform.md"

        # Check if terraform.md already exists with proper content
        if tf_doc_path.exists():
            with open(tf_doc_path, "r") as f:
                content = f.read()
                # If it already has proper documentation content, don't overwrite
                if "Terraform Infrastructure" in content and "Overview" in content:
                    self.logger.info(
                        "Terraform documentation already exists with proper content"
                    )
                    return

        content = [
            "# Terraform Infrastructure\n\n",
            "This document provides an overview of the Terraform infrastructure used in the All Things Linux project.\n\n",
            "## 🏗️ **Overview**\n\n",
            "Our Terraform configuration manages:\n\n",
            "- **Hetzner Cloud Server Provisioning**: Automated server creation\n",
            "- **Cloudflare DNS Management**: Automated DNS record creation\n",
            "- **Multi-Environment Support**: Separate staging and production configs\n",
            "- **Integration with Ansible**: Outputs used for configuration management\n\n",
            "## 📦 **Configuration Structure**\n\n",
        ]

        # Add information about terraform files found
        tf_files = list(terraform_dir.glob("*.tf"))
        if tf_files:
            content.append("### Terraform Files\n\n")
            content.append("| File | Purpose |\n")
            content.append("|------|---------||\n")

            file_descriptions = {
                "main.tf": "Provider configuration and shared resources",
                "variables.tf": "Variable definitions and descriptions",
                "outputs.tf": "Output values for Ansible integration",
                "domains.tf": "Dynamic infrastructure from domains.yml",
                "load_balancer.tf": "Load balancer configuration",
            }

            for tf_file in sorted(tf_files):
                filename = tf_file.name
                description = file_descriptions.get(filename, "Terraform configuration")
                content.append(f"| `{filename}` | {description} |\n")

            content.append("\n")

        # Add environment information
        env_dir = terraform_dir / "environments"
        if env_dir.exists():
            content.append("### Environments\n\n")
            for env in sorted(env_dir.iterdir()):
                if env.is_dir():
                    content.append(
                        f"- **{env.name.title()}**: `environments/{env.name}/terraform.tfvars`\n"
                    )
            content.append("\n")

        content.append("## 🚀 **Usage**\n\n")
        content.append("```bash\n")
        content.append("# Use our automated CLI tool (recommended)\n")
        content.append("atl apply --target infrastructure\n")
        content.append("```\n\n")
        content.append("For detailed documentation, see the infrastructure guides.\n")

        with open(tf_doc_path, "w") as f:
            f.writelines(content)

        self.logger.success(f"Terraform module index created at {tf_doc_path}")

    def generate_infrastructure_diagrams(self) -> bool:
        """Generate infrastructure visualization diagrams."""
        self.logger.info("Generating infrastructure diagrams...")
        try:
            subprocess.run(["atl", "docs", "diagrams"], check=True)
            self.logger.success("Infrastructure diagrams generated successfully.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Failed to generate infrastructure diagrams: {e}")
            if isinstance(e, subprocess.CalledProcessError):
                self.logger.error(e.stderr.decode())
            return False

    def generate_ansible_docs(self) -> bool:
        """Generate Ansible playbook and role documentation."""
        self.logger.info("Generating Ansible documentation...")

        automation_dir = self.docs_dir / "automation"
        automation_dir.mkdir(parents=True, exist_ok=True)

        # Document playbooks
        playbooks_dir = Path("playbooks")
        if playbooks_dir.exists():
            self._document_playbooks(playbooks_dir, automation_dir)

        # Document roles
        roles_dir = Path("roles")
        if roles_dir.exists():
            self._document_roles(roles_dir, automation_dir)

        # Generate inventory documentation
        self._document_inventory(automation_dir)

        return True

    def _document_playbooks(self, playbooks_dir: Path, output_dir: Path):
        """Document Ansible playbooks."""
        playbook_docs = []

        for playbook_file in playbooks_dir.glob("*.yml"):
            try:
                with open(playbook_file, "r") as f:
                    content = list(yaml.safe_load_all(f))

                for play in content:
                    if isinstance(play, list):
                        for item in play:
                            if isinstance(item, dict) and "name" in item:
                                doc = {
                                    "name": item["name"],
                                    "file": str(playbook_file),
                                    "hosts": item.get("hosts", "undefined"),
                                    "tasks": [],
                                }

                                if "tasks" in item:
                                    for task in item["tasks"]:
                                        if isinstance(task, dict) and "name" in task:
                                            doc["tasks"].append(task["name"])

                                playbook_docs.append(doc)
                    elif isinstance(play, dict) and "name" in play:
                        doc = {
                            "name": play["name"],
                            "file": str(playbook_file),
                            "hosts": play.get("hosts", "undefined"),
                            "tasks": [],
                        }

                        if "tasks" in play:
                            for task in play["tasks"]:
                                if isinstance(task, dict) and "name" in task:
                                    doc["tasks"].append(task["name"])

                        playbook_docs.append(doc)

            except Exception as e:
                self.logger.warn(f"Failed to parse playbook {playbook_file}: {e}")

        # Generate markdown documentation
        with open(output_dir / "playbooks.md", "w") as f:
            f.write("# Ansible Playbooks\n\n")
            f.write(
                "This document contains automatically generated documentation for all Ansible playbooks.\n\n"
            )

            for doc in playbook_docs:
                f.write(f"## {doc['name']}\n\n")
                f.write(f"**File**: `{doc['file']}`  \n")
                f.write(f"**Hosts**: `{doc['hosts']}`\n\n")

                if doc["tasks"]:
                    f.write("### Tasks\n\n")
                    for task in doc["tasks"]:
                        f.write(f"- {task}\n")
                    f.write("\n")

    def _document_roles(self, roles_dir: Path, output_dir: Path):
        """Document Ansible roles."""
        roles_docs = []

        for role_dir_path in roles_dir.iterdir():
            if role_dir_path.is_dir():
                role_name = role_dir_path.name
                meta_file = role_dir_path / "meta" / "main.yml"
                readme_file = role_dir_path / "README.md"

                role_doc = {
                    "name": role_name,
                    "path": str(role_dir_path),
                    "description": "No description available",
                    "has_readme": readme_file.exists(),
                }

                # Try to get description from meta/main.yml
                if meta_file.exists():
                    try:
                        with open(meta_file, "r") as f:
                            meta = yaml.safe_load(f)
                            if isinstance(meta, dict) and "galaxy_info" in meta:
                                role_doc["description"] = meta["galaxy_info"].get(
                                    "description", role_doc["description"]
                                )
                    except Exception as e:
                        self.logger.warn(
                            f"Failed to parse meta for role {role_name}: {e}"
                        )

                roles_docs.append(role_doc)

        # Generate markdown documentation
        with open(output_dir / "roles.md", "w") as f:
            f.write("# Ansible Roles\n\n")
            f.write(
                "This document contains automatically generated documentation for all Ansible roles.\n\n"
            )

            for doc in roles_docs:
                f.write(f"## {doc['name']}\n\n")
                f.write(f"**Path**: `{doc['path']}`\n\n")
                f.write(f"{doc['description']}\n\n")

                if doc["has_readme"]:
                    # Correctly reference the README from the root of the project using include-markdown-plugin
                    readme_path = Path(doc["path"]) / "README.md"
                    relative_readme_path = os.path.relpath(readme_path, output_dir)
                    f.write(f'{{!include "{relative_readme_path}"!}}\n\n')

                # List role components
                f.write("**Components**:\n")
                components = [
                    "tasks",
                    "handlers",
                    "templates",
                    "files",
                    "vars",
                    "defaults",
                    "meta",
                ]
                role_dir = Path(doc["path"])
                for component in components:
                    if (role_dir / component).exists():
                        f.write(f"- {component.capitalize()}\n")
                f.write("\n---\n\n")

    def _document_inventory(self, output_dir: Path):
        """Document Ansible inventory."""
        with open(output_dir / "inventory.md", "w") as f:
            f.write("# Ansible Inventory\n\n")
            f.write(
                "This document contains information about the Ansible inventory structure.\n\n"
            )

            # List inventory files
            inventories_dir = Path("inventories")
            if inventories_dir.exists():
                f.write("## Inventory Files\n\n")
                for inv_file in inventories_dir.glob("*"):
                    if inv_file.is_file():
                        f.write(f"- `{inv_file}`\n")
                f.write("\n")

            # List group variables
            group_vars_dir = Path("group_vars")
            if group_vars_dir.exists():
                f.write("## Group Variables\n\n")
                for var_file in group_vars_dir.glob("*.yml"):
                    f.write(f"- `{var_file}`\n")
                f.write("\n")

            # List host variables
            host_vars_dir = Path("host_vars")
            if host_vars_dir.exists():
                f.write("## Host Variables\n\n")
                for var_file in host_vars_dir.glob("*.yml"):
                    f.write(f"- `{var_file}`\n")

    def setup_mkdocs(self) -> bool:
        """Set up MkDocs configuration and structure."""
        self.logger.info("Setting up MkDocs configuration...")

        # Create docs structure
        directories = ["infrastructure", "automation", "guides", "reference", "assets"]

        for directory in directories:
            (self.docs_dir / directory).mkdir(parents=True, exist_ok=True)

        return True

    def build_docs(self, serve: bool = False) -> bool:
        """Build the complete documentation."""
        self.logger.info("Building complete infrastructure documentation...")

        # Set up directories
        if not self.setup_mkdocs():
            return False

        # Generate all documentation
        success = True
        success &= self.generate_terraform_docs()
        success &= self.generate_infrastructure_diagrams()
        success &= self.generate_ansible_docs()

        if success:
            self.logger.success("Documentation generation completed successfully!")

            if serve:
                self.logger.info("Starting MkDocs development server...")
                try:
                    subprocess.run(
                        ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"], check=True
                    )
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to start MkDocs server: {e}")
                    return False
        else:
            self.logger.error("Some documentation generation steps failed")

        return success


@click.command()
@click.option(
    "--serve", is_flag=True, help="Serve documentation locally after generation"
)
@click.option("--install-tools", is_flag=True, help="Install required external tools")
@click.option(
    "--check-deps", is_flag=True, help="Check if required tools are installed"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def cli(serve: bool, install_tools: bool, check_deps: bool, verbose: bool):
    """🔧 Generate and manage infrastructure documentation.

        This tool automatically generates comprehensive documentation for your
        infrastructure including Terraform modules, Ansible playbooks, and
        interactive infrastructure diagrams.

        Examples:
            atl docs build              # Generate all documentation
    atl docs build --serve     # Generate and serve locally
    atl status                  # Check tool dependencies
    """

    # Initialize logger
    logger = InfraLogger("docs")
    logger.banner("All Things Linux Infrastructure Documentation")

    try:
        # Initialize manager
        doc_manager = DocumentationManager(logger)

        # Handle different commands
        if install_tools:
            logger.info("Installing external documentation tools...")
            if doc_manager.install_external_tools():
                logger.success("Tools installed successfully!")
            else:
                logger.error("Failed to install some tools")
                sys.exit(1)
            return

        if check_deps:
            logger.info("Checking documentation tool dependencies...")
            if doc_manager.check_dependencies():
                logger.success("All required tools are available!")
            else:
                logger.error("Some required tools are missing")
                sys.exit(1)
            return

        # Generate documentation
        if not doc_manager.build_docs(serve=serve):
            logger.error("Documentation generation failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
