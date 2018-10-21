import os
import click

class WarehouseAddService:
    def __init__(self):
        self.env_file = os.path.join("./", ".env")

    def add(self, warehouse_name, host):
        click.secho(f'Adding new warehouse {warehouse_name}, {host}', fg="green")