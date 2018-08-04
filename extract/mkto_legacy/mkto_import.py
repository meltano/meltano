#!/usr/bin/python3
import sys
import argparse

from functools import partial
from elt.db import db_open
from elt.cli import parser_db_conn
from elt.process import integrate_csv
from config import config_table_name, config_primary_key, config_integrate


def integrate(args, **kwargs):
    with db_open() as db:
        integrate_csv(db,
                      args.input_file,
                      **config_integrate(args),
                      **kwargs)

args_func_map = {
    'create': integrate,
    'update': partial(integrate, update_action="UPDATE"),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Import a CSV file into the dataware house.")

    parser_db_conn(parser)

    parser.add_argument('action', choices=['create', 'update'], default='import',
                        help="""
create: import data in bulk from a CSV file.
update: create/update data in bulk from a CSV file.
""")

    parser.add_argument('-s', dest="source", choices=["activities", "leads"], required=True,
                        help="Specifies either leads or activies records.")

    parser.add_argument('input_file',
                        help="Specifies the file to import.")

    args = parser.parse_args()

    if not args.user or not args.password:
        print("User/Password are required.")
        sys.exit(2)

    args_func_map[args.action](args)
