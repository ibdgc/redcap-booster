import requests
import logging
from logging.handlers import RotatingFileHandler
import pathlib
from redcap_booster import config

# Log calls to REDCap API
logfile = pathlib.Path(config.settings.redcap_log)
logfile.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('redcap')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(logfile, maxBytes=1e7, backupCount=10)
formatter = logging.Formatter('%(asctime)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def redcap_api(service, config, context, payload, loginfo=None, pid=None):
    """Execute call to REDCap API"""
    
    if pid is None:
        pid = context['project_id']
    
    logger.info(f'{service}: PID {pid}: {loginfo}')
    payload['token'] = getattr(config.settings, f'token_{pid}')
    result = requests.post(f"{context['redcap_url']}/api/", payload)
    logger.info(f'RESPONSE: {result.status_code}')
    
    return result
