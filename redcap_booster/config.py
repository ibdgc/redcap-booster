from typing import List
from pydantic import BaseSettings, create_model
from pluginbase import PluginBase
import os

# Global settings (i.e., not service-specific)
class Settings(BaseSettings):
    
    plugin_dirs: List[str] = ['./redcap_services']
    pids: List[str] = []
    
    class Config:
        env_file = '.env'
        # For storing REDCap API tokens
        secrets_dir = './.secrets'
    
    @classmethod
    def with_services(cls, **field_defs):
        return create_model('FullSettings', __base__=cls, **field_defs)

# Available services provided via plugins
settings = Settings()
app_path = os.path.abspath(os.path.dirname(__file__))
plugin_base = PluginBase(package='plugins',
                         searchpath=[os.path.join(app_path,'services')])
plugins = plugin_base.make_plugin_source(searchpath=settings.plugin_dirs)

# REDCap API tokens
# Create file in secrets_dir named token_[pid] containing API token for project
field_defs = {}
for pid in settings.pids:
    field_defs[f'token_{pid}'] = (str, '')

# Service-specific settings
for service in plugins.list_plugins():
    field_defs[f'{service}'] = (dict, {})

# Service-specific settings for each project
for service in plugins.list_plugins():
    for pid in settings.pids:
        field_defs[f'{service}_{pid}'] = (dict, {})

settings = Settings.with_services(**field_defs)()
