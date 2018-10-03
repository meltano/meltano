#!/usr/bin/ python3
import json
import logging
from os import environ as env
import sys
from typing import Dict

from fire import Fire

# Set logging config
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class MarketoUtils(object):
    def __init__(self, config_dict: Dict[str, str]):
        self.config_dict = config_dict

    def generate_keyfile(self, output_file: str='marketo_keyfile.json'):
        """
        Generate a Marketo keyfile for tap-marketo.

        Pass in None as the arg for output_file if it should get returned instead
        or written out.
        """

        keyfile_mapping = {'endpoint': 'MARKETO_ENDPOINT',
                           'identity': 'MARKETO_IDENTITY',
                           'client_id': 'CLIENT_ID',
                           'client_secret': 'CLIENT_SECRET'}
        keyfile_dict = {k: self.config_dict.get(v)
                        for k, v in keyfile_mapping.items()}

        if output_file:
            with open(output_file, 'w') as keyfile:
                json.dump(keyfile_dict, keyfile, sort_keys=True, indent=2)
            logging.info('Keyfile written successfully.')
        else:
            return keyfile_dict


if __name__ == '__main__':
    marketo_utils = MarketoUtils(env.copy())
    Fire(marketo_utils)
