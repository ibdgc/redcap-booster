"""CLI tools for REDCap Booster"""

import click
from redcap_booster import config

plugins = config.plugins

@click.group()
def cli():
    """Command line utilities for managing REDCap Booster"""
    pass

@click.command()
def list_services():
    """List available services"""
    for service in plugins.list_plugins():
        click.echo(f'{service}')

@click.command()
@click.argument('service')
def list_pids(service):
    """List projects configured to use service"""
    for pid in config.settings.pids:
        if getattr(config.settings, f'{service}_{pid}'):
            click.echo(pid)

cli.add_command(list_services)
cli.add_command(list_pids)

for service in plugins.list_plugins():
    plugin = plugins.load_plugin(service)
    try:
        cli.add_command(plugin.cli)
    except AttributeError:
        pass

if __name__ == '__main__':
    cli()
