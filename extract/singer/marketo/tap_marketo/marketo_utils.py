#!/usr/bin/ python3
from datetime import datetime, timedelta
import json
import logging
from os import environ as env
import sys
from typing import Dict

from fire import Fire


class MarketoUtils(object):
    def __init__(self, config_dict: Dict[str, str]) -> None:
        self.config_dict = config_dict

    def generate_start_time(self, run_time: str, offset: int) -> str:
        """
        Generate a start_date for the keyfile.

        Expected start_time format: 2018-01-01T01:00:00.000000
        Output format: 2018-01-01T01:00:00Z
        """

        input_format = "%Y-%m-%dT%H:%M:%S.%f"
        output_format = "%Y-%m-%dT%H:%M:%SZ"
        parsed_datetime = datetime.strptime(run_time, input_format)
        raw_start_time = parsed_datetime - timedelta(minutes=offset)
        formatted_start_time = datetime.strftime(raw_start_time, output_format)

        return formatted_start_time

    def generate_keyfile(self, minute_offset: int, run_time: str, output_file: str):
        """
        Generate a Marketo keyfile for tap-marketo.

        Pass in None as the arg for output_file if it should get returned instead
        or written out.

        start_time is calculated by subtracting the offset from the run_time.

        Expected run_time format: 2018-01-01T01:00:00.000000
        Should be UTC
        """

        logging.info("Generating keyfile...")
        # Get the secret credentials from env vars
        keyfile_mapping = {
            "endpoint": "MARKETO_ENDPOINT",
            "identity": "MARKETO_IDENTITY",
            "client_id": "MARKETO_CLIENT_ID",
            "client_secret": "MARKETO_CLIENT_SECRET",
        }
        keyfile_dict = {k: self.config_dict.get(v) for k, v in keyfile_mapping.items()}

        # add the start_time
        start_time = self.generate_start_time(run_time, minute_offset)
        logging.info("Requesting data from {} onward...".format(start_time))
        keyfile_dict["start_time"] = start_time

        if output_file:
            with open(output_file, "w") as keyfile:
                json.dump(keyfile_dict, keyfile, sort_keys=True, indent=2)
            logging.info("Keyfile written to {} successfully.".format(output_file))
        else:
            return keyfile_dict
