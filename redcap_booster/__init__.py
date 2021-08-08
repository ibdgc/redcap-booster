import requests

def redcap_api(config, context, payload, pid=None):
    """Execute call to REDCap API"""
    if pid is None:
        pid = context['project_id']
    payload['token'] = getattr(config.settings, f'token_{pid}')
    return(requests.post(f"{context['redcap_url']}/api/", payload))
