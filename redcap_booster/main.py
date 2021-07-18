"""API for providing external services to REDCap"""

from fastapi import FastAPI
from starlette.requests import Request
from pluginbase import PluginBase
from redcap_booster import config
import os

app_path = os.path.abspath(os.path.dirname(__file__))
plugin_base = PluginBase(package='plugins',
                         searchpath=[os.path.join(app_path,'services')])
plugins = plugin_base.make_plugin_source(searchpath=config.settings.plugin_dirs)

app = FastAPI()

@app.post('/{service}')
async def root(service: str, request: Request):
    
    # Using Request explicitly here since the name of the [instrument]_complete
    # parameter is unknown ahead of time.
    # See https://www.starlette.io/requests/ for more information.
    context = await request.form()
    
    if service in plugins.list_plugins():
        plugin = plugins.load_plugin(service)
        plugin.run(config, context)
