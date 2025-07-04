#!/usr/bin/env python3
"""
Generates infrastructure diagrams using the built-in `terraform graph` command.
"""

import click
import subprocess
from pathlib import Path
from ..common.logging import InfraLogger


@click.command()
@click.option(
    "--output-file",
    default="docs/assets/infrastructure.svg",
    help="Path to save the output SVG file.",
)
def cli(output_file: str):
    """Generates an infrastructure diagram using Terraform."""
    logger = InfraLogger("diagrams")
    logger.banner("Infrastructure Diagram Generator")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    terraform_dir = Path("terraform")
    if not terraform_dir.exists():
        logger.error("Terraform directory not found.")
        return

    try:
        logger.info("Initializing Terraform...")
        subprocess.run(
            ["terraform", "init"], check=True, cwd=terraform_dir, capture_output=True
        )

        logger.info("Generating Terraform graph...")
        graph_dot = subprocess.check_output(
            ["terraform", "graph"], text=True, cwd=terraform_dir
        )

        logger.info(f"Rendering SVG diagram to {output_path}...")
        subprocess.run(
            ["dot", "-Tsvg"],
            input=graph_dot,
            text=True,
            check=True,
            stdout=open(output_path, "w"),
        )

        logger.success(f"Diagram saved successfully to {output_path}")

    except FileNotFoundError:
        logger.error(
            "Terraform or Graphviz (dot) not found. Please ensure they are installed and in your PATH."
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred: {e}")
        if e.stderr:
            logger.error(e.stderr)
        if e.stdout:
            logger.info(e.stdout)


if __name__ == "__main__":
    cli()
