import json

from fire import Fire

from .client import MarketoClient


def extract(config_path: str='marketo_keyfile.json'):
    """
    Handle creation of a MarketoClient instance and invoking its methods.

    config_file should be a path to a valid configuration file
    """

    with open(config_path, 'r') as config_file:
        config_dict = json.load(config_file)

    marketo_client = MarketoClient(config_dict)
    marketo_client.get_data()

def main():
    Fire(extract)

if __name__ == '__main__':
    Fire(extract)
