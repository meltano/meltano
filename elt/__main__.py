import argparse
import sys

from enum import Enum
from elt.cli import ActionEnum, OptionEnum, parser_logging
from elt.utils import setup_logging

from elt.schema.serializers.singer import SingerSerializer
from elt.schema.serializers.meltano import MeltanoSerializer


def action_convert(args):
    schema = load(, sys.stdin)
    dump(sys.stdout, schema)


class SchemaType(OptionEnum):
    MELTANO = "meltano"
    SINGER = "singer"


class Actions(ActionEnum):
    CONVERT_SCHEMA = ('convert_schema', action_convert)


def parse():
    parser = argparse.ArgumentParser(description="Use the Marketo Bulk Export to get Leads or Activities")

    parser_logging(parser)

    parser.add_argument('-s',
                        dest="source",
                        type=SchemaType,
                        choices=list(SchemaType),
                        required=True,
                        help="Specifies input schema type.")

    parser.add_argument('-d',
                        dest="destination",
                        type=SchemaType,
                        choices=list(SchemaType),
                        default=SchemaType.MELTANO,
                        help="Specifies output schema type.")

    parser.add_argument('action',
                        type=Actions.from_str,
                        choices=list(Actions),
                        default=Actions.CONVERT_SCHEMA,
                        help=("convert_schema: convert a schema into an external schema type."))

    return parser.parse_args()


def main(args):
    args.action(args)


if __name__ == '__main__':
    args = parse()

    setup_logging(args)
    main(args)
