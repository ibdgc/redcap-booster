from .db import DatabaseAccess
from .cli import commands
from redcap_booster import redcap_api
import click
import json

service = 'id_gen'
db = DatabaseAccess(service)

def generate_cli(db, commands):
    @click.group()
    @click.pass_context
    def cli(ctx):
        """Utilities for ID generation service"""
        ctx.obj = db
    
    for cmd in commands:
        cli.add_command(cmd)
    
    return cli

cli = generate_cli(db, commands)

def run(config, context, service=service, db=db):
    
    pid = context['project_id']
    id = db.get_id(pid, context['record'])
    
    # Don't go any further if an ID is not available
    if not id:
        return
    
    p_settings = getattr(config.settings, f'{service}_{pid}')
    record_id = p_settings.get('record_id', 'record_id')
    id_field = p_settings['id_field']
    
    data = json.dumps([{record_id:context['record'], id_field:id}],
                      separators=(',',':'))
    payload = {'content':'record',
               'format':'json',
               'data':data}
    
    return redcap_api(config, context, payload)
