"""Upload Completed SAE Forms to Box"""

from redcap_booster import redcap_api, box
from io import BytesIO
from datetime import datetime
import os

service = 'jcoin_sae'

def run(config, context, service=service):
    
    pid = context['project_id']
    record = context['record']
    p_settings = getattr(config.settings, f'{service}_{pid}')
    dag_fid = p_settings['dags'][context['redcap_data_access_group']]
    
    payload = {'content':'pdf',
               'record':record,
               'compactDisplay':'TRUE'}
    pdf = redcap_api(service, config, context, payload, payload).content
    
    settings_file = os.path.join(config.Settings.Config.secrets_dir,
                                 p_settings['settings_file'])
    client = box.get_client(settings_file)
    
    filename = f'{record}_{datetime.now().strftime("%Y-%m-%dT%H%M%S")}.pdf'
    folder = box.get_subfolder(record, dag_fid, client)
    client.folder(folder).upload_stream(BytesIO(pdf), filename)
