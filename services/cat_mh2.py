"""Upload CAT-MH/SUD tokens to CTIME project (CAT-MH used only at recruitment)

To do this we are reusing the ``id_gen`` service with a custom ``run()`` function.
"""

from redcap_booster.services import id_gen
from redcap_booster.services.id_gen.db import DatabaseAccess
from redcap_booster import redcap_api
import json

service = 'cat_mh2'
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
                        'catmh_interview':fields[0],
                        'catmh_id':fields[1],
                        'catmh_token':fields[2],
                        'link_to_catmh_complete':2}],
                      separators=(',',':'))
    payload = {'content':'record',
               'format':'json',
               'data':data}
    
    return redcap_api(service, config, context, payload, pid=pid)
