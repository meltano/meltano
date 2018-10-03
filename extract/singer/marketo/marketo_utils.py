#!/usr/bin/ python3
from datetime import datetime
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

    def generate_statefile(self, output_file: str='state.json',
                           start_time: str=datetime.utcnow().isoformat()):
        """
        Generate a statefile for tap-marketo for incremental loading.
        """

        endpoint_list = ['activity_types',
                         'activities',
                         'leads',
                         'lists']

        # Expected start_time format: 2018-01-01T01:00:00.000000
        input_format = '%Y-%m-%dT%H:%M:%S.%f'
        output_format = '%Y-%m-%dT%H:%M:%SZ'
        parsed_datetime = datetime.strptime(start_time, input_format)
        formatted_start_time = datetime.strftime(parsed_datetime, output_format)

        statefile_dict = {endpoint: formatted_start_time
                          for endpoint in endpoint_list}

        if output_file:
            with open(output_file, 'w') as statefile:
                json.dump(statefile_dict, statefile, sort_keys=True, indent=2)
            logging.info('Statefile written successfully.')
        else:
            return statefile_dict


if __name__ == '__main__':
    marketo_utils = MarketoUtils(env.copy())
    Fire(marketo_utils)
