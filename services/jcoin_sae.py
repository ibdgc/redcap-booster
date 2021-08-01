"""Upload Completed SAE Forms to Box"""

from redcap_booster import redcap_api
from boxsdk import JWTAuth, Client, BoxAPIException
from io import BytesIO
from logging.handlers import SysLogHandler, logging
from datetime import datetime
import os

service = 'jcoin_sae'

# Avoid Box API warnings RE existing folders (from get_prcpt_folder())
logging.basicConfig(level=logging.ERROR)

def get_prcpt_folder(context, dags, client):
    """Return ID of participant folder in Box, creating if necessary"""
    
    record = context['record']
    dag_fid = dags[context['redcap_data_access_group']]
    
    try:
        subfolder = client.folder(dag_fid).create_subfolder(record)
        return subfolder.id
    except BoxAPIException as e:
        return e.context_info['conflicts'][0]['id']

def run(config, context, service=service):
    
    pid = context['project_id']
    record = context['record']
    p_settings = getattr(config.settings, f'{service}_{pid}')
    dags = p_settings['dags']
    
    payload = {'content':'pdf',
               'record':record,
               'compactDisplay':'TRUE'}
    pdf = redcap_api(config, context, payload).content
    filename = f'{record}_{datetime.now().strftime("%Y-%m-%dT%H%M%S")}.pdf'
    
    settings_file = os.path.join(config.Settings.Config.secrets_dir,
                                 p_settings['settings_file'])
    auth = JWTAuth.from_settings_file(settings_file)
    client = Client(auth)
    
    folder = get_prcpt_folder(context, dags, client)
    client.folder(folder).upload_stream(BytesIO(pdf), filename)
