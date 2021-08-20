"""API for providing external services to REDCap"""

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from . import config
import logging
from logging.handlers import RotatingFileHandler
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
async def root(request: Request, key: str = None):
    
    # Using Request explicitly here since the name of the [instrument]_complete
    # parameter is unknown ahead of time.
    # See https://www.starlette.io/requests/ for more information.
    context = await request.form()
    logger.info(f'{request.client}: {context}')
    
    # Require API key for authentication
    pid = context.get('project_id', None)
    if not pid:
        raise HTTPException(status_code=401, detail='Project ID missing')
    api_key = getattr(config.settings, f'key_{pid}', 'Auth-Not-Yet-Configured')
    if api_key != key:
        raise HTTPException(status_code=401, detail='API key missing or invalid')
    
    for service in plugins.list_plugins():
        
        p_settings = getattr(config.settings,
                             f"{service}_{context['project_id']}", {})
        
        if 'form_triggers' in p_settings:
            if context['instrument'] in p_settings['form_triggers']:
                plugin = plugins.load_plugin(service)
                plugin.run(config, context)
