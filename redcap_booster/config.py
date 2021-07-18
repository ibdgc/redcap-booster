from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    plugin_dirs: List[str] = ['./redcap_services']
    
    class Config:
        env_file = '.env'

settings = Settings()
