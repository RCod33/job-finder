import requests


def get_jobs(url, page=None, params_extra=None):
    params = dict(params_extra or {})
    if page is not None:
        params["page"] = page

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()