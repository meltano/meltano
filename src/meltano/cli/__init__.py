from .main import cli

# import subcommands
from . import extract, schema


def main():
    cli()
