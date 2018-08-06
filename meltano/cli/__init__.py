import logging

from .main import root


def main():
    logging.basicConfig(level=logging.INFO)
    root()
