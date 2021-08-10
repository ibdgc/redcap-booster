"""Upload report to Box for use by UIC personnel"""

from redcap_booster import redcap_api
from boxsdk import JWTAuth, Client, BoxAPIException
from io import BytesIO
from logging.handlers import SysLogHandler, logging
from datetime import datetime
from PyPDF2 import PdfFileMerger, PdfFileReader
from PyPDF2.utils import PdfReadError
import os
import json
import requests

service = 'romi'

# Avoid Box API warnings RE existing folders (from get_prcpt_folder())
logging.basicConfig(level=logging.ERROR)

def get_prcpt_folder(context, fid, client):
    """Return ID of participant folder in Box, creating if necessary"""
    
    record = context['record']
    
    try:
        subfolder = client.folder(fid).create_subfolder(record)
        return subfolder.id
    except BoxAPIException as e:
        return e.context_info['conflicts'][0]['id']

def run(config, context, service=service):
    
    pid = context['project_id']
    record = context['record']
    p_settings = getattr(config.settings, f'{service}_{pid}')
    baseline = p_settings['baseline']
    catmh_id0 = p_settings['catmh_id0']
    romi_report_form = p_settings['romi_report_form']
    
    cmp = p_settings['cmp']
    record_id = p_settings['record_id']
    study_id = p_settings['study_id']
    grp = p_settings['grp']
    cmp_report_form = p_settings['cmp_report_form']
    
    # Get corresponding record_id in Case Management project
    payload = {'content':'record',
               'format':'json',
               'fields[0]':record_id,
               'fields[1]':study_id,
               'fields[2]':grp,
               'rawOrLabel':'label'}
    participants = redcap_api(config, context, payload, pid=cmp).content
    # Increase efficiency by interating in reverse order
    for p in reversed(json.loads(participants)):
        if p[study_id] == record:
            if p[grp] == 'Control':
                return
            cmp_record = p[record_id]
            break
    if not cmp_record:
        return
    
    # Get CAT-MH report
    payload = {'content':'record',
               'format':'json',
               'records':record,
               'events':baseline,
               'fields':catmh_id0}
    records = json.loads(redcap_api(config, context, payload).content)
    if records:
        interview_id = records[0][catmh_id0]
        url = p_settings['url']
        keyfile = os.path.join(config.Settings.Config.secrets_dir,
                               'catmh_report_key')
        with open(keyfile, 'r') as f:
            key = f.read().replace('\n', '')
        cat_pdf = requests.get(f'{url}/report/{interview_id}?key={key}').content
    else:
        cat_pdf = None
    
    # Retrieve PDFs
    payload = {'content':'pdf',
               'record':cmp_record,
               'instrument':cmp_report_form}
    cmp_pdf = redcap_api(config, context, payload, pid=cmp).content
    
    payload = {'content':'pdf',
               'record':record,
               'instrument':romi_report_form}
    romi_pdf = redcap_api(config, context, payload).content
    
    merger = PdfFileMerger()
    for file in [cmp_pdf, cat_pdf, romi_pdf]:
        try:
            merger.append(PdfFileReader(BytesIO(file)))
        except PdfReadError:
            pass
    pdf = BytesIO()
    merger.write(pdf)
    
    settings_file = os.path.join(config.Settings.Config.secrets_dir,
                                 p_settings['settings_file'])
    auth = JWTAuth.from_settings_file(settings_file)
    client = Client(auth)
    
    filename = f'{record}_{datetime.now().strftime("%Y-%m-%dT%H%M%S")}.pdf'
    folder = get_prcpt_folder(context, p_settings['box_folder'], client)
    client.folder(folder).upload_stream(pdf, filename)
