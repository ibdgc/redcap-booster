"""Utilities for interacting with Box API"""

from boxsdk import JWTAuth, Client, BoxAPIException
import logging
from logging.handlers import RotatingFileHandler
import pathlib
from . import config

# Log all calls to Box API using SDK's built-in logging (at INFO level)
logfile = pathlib.Path(config.settings.box_log)
logfile.parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('boxsdk.network')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(logfile, maxBytes=1e7, backupCount=10)
logger.addHandler(handler)

def get_client(settings_file):
    """Return client for Box API"""
    
    auth = JWTAuth.from_settings_file(settings_file)
    client = Client(auth)
    return client

def get_subfolder(name, parent, client):
    """Return ID of Box subfolder, creating if necessary"""
    
    try:
        subfolder = client.folder(parent).create_subfolder(name)
        return subfolder.id
    except BoxAPIException as e:
        return e.context_info['conflicts'][0]['id']
