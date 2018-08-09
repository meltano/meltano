import logging

from .main import cli


def main():
    logging.basicConfig(level=logging.INFO)
    cli()

