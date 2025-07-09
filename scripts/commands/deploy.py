#!/usr/bin/env python3
"""
All Things Linux Infrastructure Deployment Script
Python version of the bash deploy.sh script with enhanced features
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from ..common.config import ConfigManager
from ..common.logging import InfraLogger


class DeploymentManager:
    """Main deployment manager"""

    def __init__(self, project_root: Path, logger: InfraLogger):
        self.project_root = project_root
        self.logger = logger
        self.config_manager = ConfigManager(project_root, logger)
        self.console = Console()

    def run_terraform(
        self, action: str, environment: str, auto_approve: bool = False
    ) -> bool:
        """Run Terraform operations"""
        self.logger.info(f"Running Terraform {action} for {environment} environment...")

        terraform_dir = self.project_root / "terraform"

        try:
            # Change to terraform directory
            os.chdir(terraform_dir)

            # Initialize Terraform
            subprocess.run(["terraform", "init"], check=True)

            # Select or create workspace
            try:
                subprocess.run(
                    ["terraform", "workspace", "select", environment],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["terraform", "workspace", "new", environment], check=True
                )

            # Run the terraform action
            cmd = ["terraform", action, f"-var=environment={environment}"]

            if auto_approve and action in ["apply", "destroy"]:
                cmd.append("-auto-approve")

            result = subprocess.run(cmd, check=True)

            self.logger.success(f"Terraform {action} completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Terraform {action} failed: {e}")
            return False
        finally:
            # Change back to project root
            os.chdir(self.project_root)

    def run_ansible(
        self,
        target: str,
        verbose: bool = False,
        dry_run: bool = False,
        domain_name: Optional[str] = None,
    ) -> bool:
        """Run Ansible operations"""
        self.logger.info(f"Running Ansible for target: {target}")

        try:
            os.chdir(self.project_root)

            cmd = ["ansible-playbook"]
            inventory = "inventories/dynamic.py"

            if verbose:
                cmd.append("-vvv")

            if dry_run:
                cmd.extend(["--check", "--diff"])

            # Determine playbook and additional options
            if target == "all":
                cmd.extend(["playbooks/site.yml", "-i", inventory])
            elif target == "domains":
                cmd.extend(["playbooks/dynamic-deploy.yml", "-i", inventory])
            elif target == "domain":
                if not domain_name:
                    self.logger.error("Domain name required for domain deployment")
                    return False
                cmd.extend(
                    [
                        "playbooks/domains/generic-domain.yml",
                        "-i",
                        inventory,
                        "--limit",
                        domain_name,
                        "--extra-vars",
                        f"target_domain={domain_name}",
                    ]
                )
            elif target == "infrastructure":
                cmd.extend(["playbooks/infrastructure/bootstrap.yml", "-i", inventory])
            else:
                self.logger.error(f"Unknown Ansible target: {target}")
                return False

            # Run ansible-playbook
            result = subprocess.run(cmd, check=True)

            self.logger.success(f"Ansible {target} completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Ansible {target} failed: {e}")
            return False

    def run_syntax_check(self) -> bool:
        """Run Ansible syntax check"""
        self.logger.info("Running syntax checks...")

        try:
            os.chdir(self.project_root)

            cmd = ["ansible-playbook", "playbooks/site.yml", "--syntax-check"]
            subprocess.run(cmd, check=True)

            self.logger.success("Syntax check passed")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Syntax check failed: {e}")
            return False

    def run_lint(self) -> bool:
        """Run linting checks"""
        self.logger.info("Running linting checks...")

        lint_script = self.project_root / "scripts" / "lint.sh"

        try:
            result = subprocess.run([str(lint_script), "--strict"], check=True)
            self.logger.success("Linting completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Linting failed: {e}")
            return False


# Click CLI interface
@click.group()
@click.option(
    "--environment",
    "-e",
    default="development",
    help="Target environment (development/staging/production)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be deployed")
@click.pass_context
def cli(ctx, environment, verbose, dry_run):
    """All Things Linux Infrastructure Deployment

    Unified deployment interface for Terraform + Ansible with uv integration
    """
    # Setup context
    ctx.ensure_object(dict)
    ctx.obj["environment"] = environment
    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run

    # Initialize logger
    project_root = Path(__file__).parent.parent
    logger = InfraLogger("deploy", project_root / "logs")
    ctx.obj["logger"] = logger
    ctx.obj["project_root"] = project_root

    # Show banner
    logger.banner(
        "All Things Linux Infrastructure Deployment",
        "Unified Terraform + Ansible with uv",
    )

    # Initialize deployment manager
    ctx.obj["deployment_manager"] = DeploymentManager(project_root, logger)


@cli.command()
@click.option(
    "--target",
    "-t",
    default="all",
    type=click.Choice(["all", "infrastructure", "domains", "domain"]),
    help="Deployment target",
)
@click.option("--domain-name", help="Domain name for domain-specific deployment")
@click.option("--ansible-only", is_flag=True, help="Run only Ansible configuration")
@click.option("--terraform-only", is_flag=True, help="Run only Terraform provisioning")
@click.pass_context
def plan(ctx, target, domain_name, ansible_only, terraform_only):
    """Plan infrastructure changes (default action)"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    # Check prerequisites
    if not deployment_manager.config_manager.check_prerequisites():
        sys.exit(1)

    logger.info(f"Planning deployment for {ctx.obj['environment']} environment")
    logger.info(f"Target: {target}")

    success = True

    # Run Terraform plan
    if not ansible_only:
        if not deployment_manager.run_terraform("plan", ctx.obj["environment"]):
            success = False

    # Run Ansible (dry run for plan)
    if not terraform_only and success:
        if not deployment_manager.run_ansible(
            target,
            ctx.obj["verbose"],
            dry_run=True,  # Always dry run for plan
            domain_name=domain_name,
        ):
            success = False

    if success:
        logger.success("Planning completed successfully")
    else:
        logger.error("Planning failed")
        sys.exit(1)


@cli.command()
@click.option(
    "--target",
    "-t",
    default="all",
    type=click.Choice(["all", "infrastructure", "domains", "domain"]),
    help="Deployment target",
)
@click.option("--domain-name", help="Domain name for domain-specific deployment")
@click.option("--auto-approve", "-y", is_flag=True, help="Auto-approve changes")
@click.option("--ansible-only", is_flag=True, help="Run only Ansible configuration")
@click.option("--terraform-only", is_flag=True, help="Run only Terraform provisioning")
@click.pass_context
def apply(ctx, target, domain_name, auto_approve, ansible_only, terraform_only):
    """Apply infrastructure and configuration"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    # Check prerequisites
    if not deployment_manager.config_manager.check_prerequisites():
        sys.exit(1)

    # Check environment variables
    if not deployment_manager.config_manager.check_environment_variables(
        "apply", terraform_only
    ):
        sys.exit(1)

    logger.info(f"Applying deployment for {ctx.obj['environment']} environment")
    logger.info(f"Target: {target}")

    success = True

    # Run Terraform apply
    if not ansible_only:
        if not deployment_manager.run_terraform(
            "apply", ctx.obj["environment"], auto_approve
        ):
            success = False

    # Run Ansible
    if not terraform_only and success:
        if not deployment_manager.run_ansible(
            target, ctx.obj["verbose"], ctx.obj["dry_run"], domain_name=domain_name
        ):
            success = False

    if success:
        logger.success("Deployment completed successfully")
    else:
        logger.error("Deployment failed")
        sys.exit(1)


@cli.command()
@click.option("--auto-approve", "-y", is_flag=True, help="Auto-approve destruction")
@click.pass_context
def destroy(ctx, auto_approve):
    """Destroy infrastructure (use with caution)"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    environment = ctx.obj["environment"]

    logger.warn(f"This will destroy infrastructure in {environment} environment!")

    if not auto_approve:
        if not click.confirm("Are you sure you want to continue?"):
            logger.info("Destruction cancelled")
            return

    # Check prerequisites
    if not deployment_manager.config_manager.check_prerequisites():
        sys.exit(1)

    if not deployment_manager.run_terraform("destroy", environment, auto_approve):
        logger.error("Destruction failed")
        sys.exit(1)

    logger.success("Infrastructure destroyed successfully")


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    deployment_manager.config_manager.show_config()


@cli.command()
@click.argument("domain_name")
@click.pass_context
def enable(ctx, domain_name):
    """Enable a domain"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    if deployment_manager.config_manager.toggle_domain(domain_name, True):
        logger.success(f"Domain {domain_name} enabled")
    else:
        sys.exit(1)


@cli.command()
@click.argument("domain_name")
@click.pass_context
def disable(ctx, domain_name):
    """Disable a domain"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    if deployment_manager.config_manager.toggle_domain(domain_name, False):
        logger.success(f"Domain {domain_name} disabled")
    else:
        sys.exit(1)


@cli.command()
@click.pass_context
def check(ctx):
    """Run syntax check only"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    if not deployment_manager.run_syntax_check():
        sys.exit(1)


@cli.command()
@click.pass_context
def lint(ctx):
    """Run linting before deployment"""
    logger = ctx.obj["logger"]
    deployment_manager = ctx.obj["deployment_manager"]

    if not deployment_manager.run_lint():
        sys.exit(1)


if __name__ == "__main__":
    cli()
