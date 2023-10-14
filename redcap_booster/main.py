"""API for providing external services to REDCap"""

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Optional
from redcap_booster import config
import logging
from logging.handlers import RotatingFileHandler
from secrets import compare_digest
import pathlib

# Log requests
logfile = pathlib.Path(config.settings.request_log)
logfile.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('request')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(logfile, maxBytes=1e7, backupCount=10)
formatter = logging.Formatter('%(asctime)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

plugins = config.plugins
app = FastAPI(root_path=config.settings.root_path)

@app.post('/')
async def root(request: Request, key: Optional[str] = ''):
    
    # Using Request explicitly here since the name of the [instrument]_complete
    # parameter is unknown ahead of time.
    # See https://www.starlette.io/requests/ for more information.
    context = await request.form()
    logger.info(f'{request.client}: {context}')
    
    # Require API key for authentication
    pid = context.get('project_id', None)
    if not pid:
        raise HTTPException(status_code=401, detail='Project ID missing')
    api_key = getattr(config.settings, f'key_{pid}', '')
    if not key or not compare_digest(key, api_key):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail='API key missing or invalid'
        )
    
    for service in plugins.list_plugins():
        
        p_settings = getattr(config.settings,
                             f"{service}_{context['project_id']}", {})
        
        if 'form_triggers' in p_settings:
            if context['instrument'] in p_settings['form_triggers']:
                plugin = plugins.load_plugin(service)
                plugin.run(config, context)
