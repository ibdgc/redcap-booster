"""CLI utilities for ID generation service"""

import click
import csv
import sys
from redcap_booster import config, redcap_api
from redcap_booster.services import id_gen
import json

@click.command()
@click.argument('pid')
@click.argument('filename', type=click.File('r'))
@click.option('--random-order/--no-random-order', default=False,
              show_default=True, help='Randomize order of IDs')
@click.pass_obj
def load_ids(db, pid, filename, random_order):
    """Load IDs from file"""
    ids = filename.read().splitlines()
    if len(ids)!=len(set(ids)):
        sys.exit(f'"{filename.name}" contains duplicate IDs')
    db.load_ids(pid, ids, random_order)

@click.command()
@click.argument('pid')
@click.argument('filename', type=click.File('r'))
@click.pass_obj
def import_map(db, pid, filename):
    """Import existing map into empty table
    
    FILENAME should be a CSV file with header "id,record".
    """
    reader = csv.reader(filename)
    row = next(reader)
    if row[0]!='id' or row[1]!='record':
        sys.exit(f'First row invalid; expected header "id,record"')
    
    lineno = 1
    ids, records, map = [], [], []
    for row in reader:
        
        lineno += 1
        if not row[0] or not row[1]:
            sys.exit(f'ID and/or REDCap record missing on line {lineno}')
        
        ids.append(row[0])
        records.append(row[1])
        map.append((row[0],row[1]))
    
    if len(ids)!=len(set(ids)):
        sys.exit('Duplicate IDs found')
    elif len(records)!=len(set(records)):
        sys.exit('Duplicate REDCap records found')
    
    db.import_map(pid, map)

@click.command()
@click.argument('pid')
@click.argument('filename', type=click.File('w'))
@click.option('--exclude-unused/--no-exclude-unused', default=True,
              show_default=True, help='Exclude unused IDs')
@click.pass_obj
def export_map(db, pid, filename, exclude_unused):
    """Export CSV file mapping IDs to REDCap records"""
    map = db.export_map(pid)
    
    if exclude_unused:
        map = [row for row in map if row[1]]
    
    csv_file = csv.writer(filename)
    csv_file.writerow(('id','record'))
    csv_file.writerows(map)

@click.command()
@click.argument('pid')
@click.argument('redcap_url')
@click.pass_obj
def refresh_ids(db, pid, redcap_url):
    """Refresh all IDs for a given project
    
    May be used to assign IDs for existing records that do not yet have them.
    """
    p_settings = getattr(config.settings, f'{id_gen.service}_{pid}')
    record_id = p_settings.get('record_id', 'record_id')
    id_field = p_settings['id_field']
    
    context = dict(project_id=pid, redcap_url=redcap_url)
    payload = {'content':'record', 'format':'json', 'fields':[record_id]}
    records = redcap_api(id_gen.service, config, context, payload, payload).json()
    
    data = []
    done = []
    for record in records:
        if record[record_id] not in done:
            data.append({record_id:record[record_id],
                         id_field:db.get_id(pid, record[record_id])})
            done.append(record[record_id])
    
    payload = {'content':'record',
               'format':'json',
               'data':json.dumps(data, separators=(',',':'))}
    
    result = redcap_api(id_gen.service, config, context, payload, payload)
    print(f'{result.json()["count"]} records refreshed')

commands = [load_ids, import_map, export_map, refresh_ids]
