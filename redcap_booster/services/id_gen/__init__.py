from .cli import cli
from .db import get_id
import json
from redcap_booster import redcap_api

def run(config, context):
    
    pid = context['project_id']
    id = get_id(pid, context['record'])
    
    # Don't go any further if an ID is not available
    if not id:
        return
    
    p_settings = getattr(config.settings, f'id_gen_{pid}')
    record_id = getattr(p_settings, 'record_id', 'record_id')
    id_field = p_settings['id_field']
    
    data = json.dumps([{record_id:context['record'], id_field:id}],
                      separators=(',',':'))
    payload = {'content':'record',
               'format':'json',
               'data':data}
    
    return redcap_api(config, context, payload)
