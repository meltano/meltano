#!/usr/bin/env python3

import sys
import pandas as pd

from logging import info, error, basicConfig
from os import environ as env, remove
from typing import List, Dict
from fire import Fire
from stringcase import snakecase


def parse_html_table(html_source: str, table_num: int=0) -> pd.DataFrame:
    """
    Parses an HTML table into a DataFrame. This function assumes that the
    first row of the table is the column headers.

    Only grabbing the Name and Type columns because that is all the
    schema needs.

    html_source can either be a string or a URL.

    table_num tells pandas which table to use on the page. The tables are
    usually ordered from top to bottom.
    """

    return pd.read_html(html_source, header=0)[table_num][['Name', 'Type']]


def schema_formatter(raw_df: pd.DataFrame) -> Dict[str, str]:
    """
    Creates a dataframe in the right format to be used to generate a valid
    valid schema file.

    The output DataFrame has the following columns:
        in: the original column names
        out: column names converted into snake_case from CamelCase
        type: Proper version of the original type
    """

    raw_df.columns = ['in', 'type']
    raw_df['type'] = raw_df['type'].apply(lambda x: x.capitalize())
    raw_df['out']  = raw_df['in'].apply(lambda x: snakecase(x))

    return raw_df[['in', 'out', 'type']].to_dict('records')


def schema_printer(schema_list: List[Dict[str, str]]) -> None:
    """
    Print the schema out so that it can be easily pasted elsewhere.

    Hardcoded to follow the format required by the schema.py files
    """

    schema_format = "'in': '{in}', 'out': '{out}', 'type':'{type}'"
    for schema in schema_list:
        print('{' + schema_format.format(**schema) + '},')

    return


def main(args: List[str]) -> None:
    """
    Take a URL or raw HTML and print the table from it in the format of the
    netsuite schema files.
    """

    html_source = args[1]
    parsed_table = parse_html_table(html_source)
    schema_list = schema_formatter(parsed_table.copy())
    schema_printer(schema_list)

if __name__ == '__main__':
    main(sys.argv)
