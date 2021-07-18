"""API for providing external services to REDCap"""

from fastapi import FastAPI
from starlette.requests import Request
from redcap_booster import config

plugins = config.plugins
app = FastAPI()

@app.post('/')
async def root(request: Request):
    
    # Using Request explicitly here since the name of the [instrument]_complete
    # parameter is unknown ahead of time.
    # See https://www.starlette.io/requests/ for more information.
    context = await request.form()
    
    for service in plugins.list_plugins():
        
        pids = config.settings.pids
        if context['project_id'] in pids:
            p_settings = getattr(config.settings,
                                 f"{service}_{context['project_id']}")
            form_triggers = p_settings['form_triggers']
            
            if context['instrument'] in form_triggers:
                plugin = plugins.load_plugin(service)
                plugin.run(config, context)
