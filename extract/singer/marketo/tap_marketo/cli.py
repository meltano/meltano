import json
import logging
import sys

from fire import Fire
from os import environ as env

from .client import MarketoClient
from .marketo_utils import MarketoUtils


# Set logging config
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def extract(config_path: str = "marketo_keyfile.json"):
    """
    Handle creation of a MarketoClient instance and invoking its methods.

    config_file should be a path to a valid configuration file
    """

    with open(config_path, "r") as config_file:
        config_dict = json.load(config_file)

    marketo_client = MarketoClient(config_dict)
    marketo_client.get_data()


def create_keyfile(keyfile_path: str = "marketo_keyfile.json"):
    """
    Create the keyfile from env vars.
    """

    marketo_utils = MarketoUtils(env.copy())
    marketo_utils.generate_keyfile()


def main():
    Fire({"extract": extract, "create_keyfile": create_keyfile})
