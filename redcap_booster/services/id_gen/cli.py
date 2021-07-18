"""CLI utilities for ID generation service"""

import click
from . import db
import csv

@click.group('id-gen')
def cli():
    """Utilities for ID generation service
    
    To configure service, add the following to .env file:
    
        id_gen = '{"db":"[database]"}'
    
    For each project, add:
    
        id_gen_[pid] = '{"form_triggers":[[form], ...], "id_field":"[field]"}'
    """
    pass

@click.command()
@click.argument('pid')
@click.argument('filename', type=click.File('r'))
@click.option('--random-order/--no-random-order', default=False,
              show_default=True, help='Randomize order of IDs')
def load_ids(pid, filename, random_order):
    """Load IDs from file"""
    ids = filename.read().splitlines()
    db.load_ids(pid, ids, random_order)

@click.command()
@click.argument('pid')
@click.argument('filename', type=click.File('w'))
@click.option('--exclude-unused/--no-exclude-unused', default=True,
              show_default=True, help='Exclude unused IDs')
def export_map(pid, filename, exclude_unused):
    """Export CSV file mapping IDs to REDCap records"""
    map = db.get_map(pid)
    
    if exclude_unused:
        map = [row for row in map if row[1]]
    
    csv_file = csv.writer(filename)
    csv_file.writerow(('id','record'))
    csv_file.writerows(map)

cli.add_command(load_ids)
cli.add_command(export_map)
