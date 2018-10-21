import os
import yaml
import click
from meltano.support.warehouse_add_service import WarehouseAddService
from urllib.parse import urlparse
from . import cli

@cli.command()
@click.option('--name', prompt='Warehouse name')
@click.option('--host', prompt='Warehouse host')
def connect(name, host):
    warehouse_service = WarehouseAddService()
    warehouse_service.add(name, host)
    
