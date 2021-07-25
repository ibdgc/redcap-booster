"""API for providing external services to REDCap"""

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from redcap_booster import config

plugins = config.plugins
app = FastAPI(root_path=config.settings.root_path)

@app.post('/')
async def root(request: Request, key: str = None):
    
    # Using Request explicitly here since the name of the [instrument]_complete
    # parameter is unknown ahead of time.
    # See https://www.starlette.io/requests/ for more information.
    context = await request.form()
    
    # Require API key for authentication
    pid = context['project_id']
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
