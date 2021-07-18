import requests

def redcap_api(config, context, payload):
    """Execute call to REDCap API"""
    pid = context['project_id']
    payload['token'] = getattr(config.settings, f'token_{pid}')
    return(requests.post(f"{context['redcap_url']}/api/", payload))
