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
        id0,token0,id3,token3,id6,token6,id9,token9,id12,token12 = tokens.split(',')
    
    p_settings = getattr(config.settings, f'{service}_{pid}')
    record_id = p_settings.get('record_id', 'record_id')
    
    data = json.dumps([{record_id:context['record'],
                        'catmh_id0':id0,
                        'catmh_token0':token0,
                        'catmh_id3':id3,
                        'catmh_token3':token3,
                        'catmh_id6':id6,
                        'catmh_token6':token6,
                        'catmh_id9':id9,
                        'catmh_token9':token9,
                        'catmh_id12':id12,
                        'catmh_token12':token12,
                        'catmh_tokens_complete':2}],
                      separators=(',',':'))
    payload = {'content':'record',
               'format':'json',
               'data':data}
    
    return redcap_api(service, config, context, payload, record_id:context['record'])
