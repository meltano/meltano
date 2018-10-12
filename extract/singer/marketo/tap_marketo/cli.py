from datetime import datetime
import json
import logging
import sys
from typing import Dict

from fire import Fire
from os import environ as env
from pandas.io.json import build_table_schema
import singer

from .client import MarketoClient
from .marketo_utils import MarketoUtils


# Set logging config
logger = singer.get_logger()

CONFIG_PATH = "marketo_keyfile.json"


def extract(config: str = CONFIG_PATH, log_only: bool = False):
    """
    Handle creation of a MarketoClient instance and invoking its methods.

    config_file should be a path to a valid configuration file
    """
    with open(config, "r") as config_file:
        config_dict = json.load(config_file)

    marketo_client = MarketoClient(config_dict)
    marketo_data: Dict = marketo_client.get_all()

    if log_only:
        for endpoint, dataframe in marketo_data.items():
            logging.info(f"Columns for endpoint: {endpoint}")
            logging.info(dataframe.columns)
            logging.info(f"Sample data for endpoint: {endpoint}")
            logging.info(dataframe.head())
    else:
        for endpoint, dataframe in marketo_data.items():
            singer.write_schema(
                stream_name=endpoint,
                schema={"properties": build_table_schema(dataframe, primary_key="id")},
                key_properties=["id"],
            )
            singer.write_records(
                stream_name=endpoint, records=dataframe.to_dict(orient="records")
            )


def create_keyfile(
    config_path: str = CONFIG_PATH,
    minute_offset: str = "70",
    run_time: str = datetime.utcnow().isoformat(),
):
    """
    Create the keyfile from env vars.
    """
    marketo_utils = MarketoUtils(env.copy())
    marketo_utils.generate_keyfile(
        output_file=config_path, run_time=run_time, minute_offset=int(minute_offset)
    )


def main():
    Fire({"extract": extract, "create_keyfile": create_keyfile})
