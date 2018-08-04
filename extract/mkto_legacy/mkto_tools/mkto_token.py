#!/usr/bin/python3
import os
import requests

from elt.error import ExtractError


mk_endpoint = os.environ.get('MKTO_ENDPOINT')
mk_client_id = os.environ.get('MKTO_CLIENT_ID')
mk_client_secret = os.environ.get('MKTO_CLIENT_SECRET')


def get_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": mk_client_id,
        "client_secret": mk_client_secret
    }

    token_url = "{}identity/oauth/token".format(mk_endpoint)
    response = requests.get(token_url, params=payload)

    if response.status_code == 200:
        r_json = response.json()
        token = r_json.get("access_token", None)
        return token
    else:
        raise ExtractError("Cannot fetch access token: {}".format(response.body))
