import os
from importlib import import_module
from typing import Dict
import yaml

from sqlalchemy import (
    MetaData,
    Table,
    String,
    Column,
    TIMESTAMP,
    Float,
    Integer,
    Boolean,
    Date,
    REAL,
    SMALLINT,
    TEXT,
    BIGINT,
    JSON,
)


def get_sqlalchemy_col(field_name: str, field_type_name: str) -> Column:
    if field_type_name == 'timestamp without time zone':
        return Column(field_name, TIMESTAMP(timezone=False))
    elif field_type_name == 'timestamp with time zone':
        return Column(field_name, TIMESTAMP(timezone=True))
    elif field_type_name == 'character varying':
        return Column(field_name, String)
    elif field_type_name == 'date':
        return Column(field_name, Date)
    elif field_type_name == 'real':
        return Column(field_name, REAL)
    elif field_type_name == 'integer':
        return Column(field_name, Integer)
    elif field_type_name == 'smallint':
        return Column(field_name, SMALLINT)
    elif field_type_name == 'text':
        return Column(field_name, TEXT)
    elif field_type_name == 'bigint':
        return Column(field_name, BIGINT)
    elif field_type_name == 'float':
        return Column(field_name, Float)
    elif field_type_name == 'boolean':
        return Column(field_name, Boolean)
    elif field_type_name == 'json':
        return Column(field_name, JSON)
    # elif field_type_name == '':
    #     return Column(field_name, )
    print((f'{field_type_name} is unknown column type'))
    raise NotImplemented


def tables_from_manifest(
        manifest_file_path: str,
        metadata: MetaData,
        schema_name: str,
) -> {str: Table}:
    with open(manifest_file_path) as file:
        schema_manifest: dict = yaml.load(file)
        tables = {}
        for table_name in schema_manifest:
            columns: {str: str} = schema_manifest[table_name]['columns']
            columns_list = [
                get_sqlalchemy_col(field_name, field_type_name)
                for field_name, field_type_name in columns.items()
            ]
            table = Table(
                table_name,
                metadata,
                *columns_list,
                schema=schema_name,
            )
            tables[table_name] = table
    return tables


def import_class(registry_path, dir_name, prefix) -> object:
    """

    :param registry_path: name of the registry to load from (e.g. extract, load)
    :param dir_name: Name of the individual extractor or loader
    :param prefix: Prefix used for its class name (e.g. Loader, Extractor)
    :return:
    """
    module = import_module('.'.join([registry_path, dir_name]))
    return getattr(module, f'{dir_name}{prefix}')


def get_registry(registry_path: str, prefix: str) -> Dict[str, object]:
    """
    Helper method that searches registry_path and returns registry dict
    :param prefix:
    :param registry_path: path to the registry folder (should be folders with loaders or extractors)
    :return:  a dictionary like:
        {
            'Demo': <class 'extract.Demo.DemoExtractor'>,
            'Fastly': <class 'extract.Fastly.FastlyExtractor'>,
            'Sfdc': <class 'extract.Sfdc.extractor.SfdcExtractor'>
        }
    """
    with os.scandir(registry_path) as DirEntries:
        registry_folders = [
            entry for entry in DirEntries
            if entry.is_dir() and not entry.name.startswith(('__', '.'))
        ]
        return {
            dir_entry.name: import_class(registry_path, dir_entry.name, prefix)
            for dir_entry in registry_folders
        }


EXTRACTORS_DIR = 'extract'
LOADERS_DIR = 'load'
EXTRACT_CLASS_PREFIX = 'Extractor'
LOAD_CLASS_PREFIX = 'Loader'

EXTRACTOR_REGISTRY = get_registry(EXTRACTORS_DIR, EXTRACT_CLASS_PREFIX)
LOADER_REGISTRY = get_registry(LOADERS_DIR, LOAD_CLASS_PREFIX)
