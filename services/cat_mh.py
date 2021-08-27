"""Upload CAT-MH/SUD tokens to REDCap project

To do this we are reusing the ``id_gen`` service with a custom ``run()`` function.
"""

from redcap_booster.services import id_gen
from redcap_booster.services.id_gen.db import DatabaseAccess
from redcap_booster import redcap_api
import json

service = 'cat_mh'
db = DatabaseAccess(service)

cli = id_gen.generate_cli(db, id_gen.commands)

def run(config, context, service=service, db=db):
    
    pid = context['project_id']
    tokens = db.get_id(pid, context['record'])
    
    if not tokens:
        return
    else:
        fields = tokens.split(',')
    
    p_settings = getattr(config.settings, f'{service}_{pid}')
    record_id = p_settings.get('record_id', 'record_id')
    
    data = json.dumps([{record_id:context['record'],
                        'catmh_interview0':fields[0],
                        'catmh_id0':fields[1],
                        'catmh_token0':fields[2],
                        'catmh_interview3':fields[3],
                        'catmh_id3':fields[4],
                        'catmh_token3':fields[5],
                        'catmh_interview6':fields[6],
                        'catmh_id6':fields[7],
                        'catmh_token6':fields[8],
                        'catmh_interview9':fields[9],
                        'catmh_id9':fields[10],
                        'catmh_token9':fields[11],
                        'catmh_interview12':fields[12],
                        'catmh_id12':fields[13],
                        'catmh_token12':fields[14],
                        'catmh_tokens_complete':2}],
                      separators=(',',':'))
    payload = {'content':'record',
               'format':'json',
               'data':data}
    
    return redcap_api(service, config, context, payload, pid=pid)
