
import logging
from typing import Dict
import sys

import aiohttp
from fire import Fire
import requests

# Set the logging config
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class MarketoClient(object):
    def __init__(self, config: Dict[str,str]):
        self.endpoint = config.get('endpoint')
        self.identity = config.get('identity')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.start_time = config.get('start_time')
        self.access_token = self.get_access_token()
        self.initial_date_token = self.get_date_token()

    def get_response(self, url: str, payload: Dict[str,str]):
        """
        Boilerplate for GETting a request and returning the json.
        """

        # Try to get the access token, it may not exist yet
        try:
            auth = {'access_token': self.access_token}
        except:
            auth = {'access_token': 'None'}

        params = {**auth, **payload}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.critical(response.status_code)
            logging.critical(response.text)
            sys.exit(1)
        else:
            return response.json()

    def get_access_token(self) -> str:
        """
        Hit the Marketo Identity endpoint to get a valid access token.
        """

        identity_url = '{}/oauth/token'.format(self.identity)
        payload = {'grant_type': 'client_credentials',
                   'client_id': self.client_id,
                   'client_secret': self.client_secret}

        return self.get_response(identity_url, payload)['access_token']

    def get_date_token(self) -> str:
        """
        Get a date-based paging token from Marketo for use in other calls.
        """

        token_url = '{}/v1/activities/pagingtoken.json'.format(self.endpoint)
        payload = {'sinceDatetime': self.start_time}
        response = self.get_response(token_url, payload)

        if not response['success']:
            logging.critical('Failed to get initial nextPageToken.')
            logging.critical(response['errors'])
            sys.exit(1)
        else:
            return response['nextPageToken']

    def get_activity_types(self):
        """
        Get the full list of activity types.
        """

        return

    def get_leads(self):
        return
