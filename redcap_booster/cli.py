"""CLI tools for REDCap Booster"""

import click
from pluginbase import PluginBase
from redcap_booster import config
import os

app_path = os.path.abspath(os.path.dirname(__file__))
plugin_base = PluginBase(package='plugins',
                         searchpath=[os.path.join(app_path,'services')])
plugins = plugin_base.make_plugin_source(searchpath=config.settings.plugin_dirs)

@click.group()
def cli():
    """Command line utilities for managing REDCap Booster"""
    pass

@click.command()
def list_services():
    """List available services"""
    for service in plugins.list_plugins():
        click.echo(f'{service}')

cli.add_command(list_services)

for service in plugins.list_plugins():
    plugin = plugins.load_plugin(service)
    try:
        cli.add_command(plugin.cli)
    except AttributeError:
        pass

if __name__ == '__main__':
    cli()
