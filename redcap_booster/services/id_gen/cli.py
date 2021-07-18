"""CLI utilities for ID generation service"""

import click

@click.group('id-gen')
def cli():
    """Utilities for ID generation service"""
    pass

@click.command()
def list_projects():
    """List REDCap projects configured to use service"""
    click.echo('We have a lot of projects!')

cli.add_command(list_projects)
