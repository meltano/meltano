import json
from typing import Dict
import sys

import aiohttp
import requests


class MarketoClient(object):
    def __init__(self, config: Dict[str,str]):
        self.endpoint = config.get('endpoint')
        self.identity = config.get('identity')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.start_time = config.get('start_time')

    def get_access_token(self) -> str:
        """
        Hit the Marketo Identity endpoint to get a valid access token.
        """

        identity_url = '{}/oauth/token'.format(self.identity)
        payload = {'grant_type': 'client_credentials',
                   'client_id': self.client_id,
                   'client_secret': self.client_secret}
        response = requests.get(identity_url, params=payload)

        print(response.json())




def main(config_path: str):
    """
    Handle creation of a MarketoClient instance and invoking its methods.

    config_file should be a path to a valid configuration file
    """

    with open(config_path, 'r') as config_file:
        config_dict = json.load(config_file)

    print(config_dict)



if __name__ == '__main__':
    Fire(main)
