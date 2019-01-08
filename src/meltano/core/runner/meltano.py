import importlib
import click
import logging

from meltano.core.error import Error
from . import Runner


# TODO: to be generated from the file structure of /Extract/
EXTRACTOR_REGISTRY = {
    "fastly": ("meltano.plugins.fastly.extractor", "FastlyExtractor"),
    "sfdc": ("meltano.plugins.sfdc", "SfdcExtractor"),
}

LOADER_REGISTRY = {
    "postgres": ("meltano.plugins.postgres_loader", "PostgresLoader"),
    "csv": ("meltano.plugins.csv_loader", "CsvLoader"),
    "snowflake": ("meltano.plugins.snowflake.loader", "SnowflakeLoader"),
}


class MeltanoRunner(Runner):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def import_cls(cls, registry):
        mod_name, cls_name = registry
        try:
            mod = importlib.import_module(mod_name)
            return getattr(mod, cls_name)
        except (ImportError, NameError) as err:
            logging.debug(err)

    def run(self, extractor_name, loader_name):
        click.echo(f"Loading and initializing extractor: {extractor_name}")
        extractor_class = self.import_cls(EXTRACTOR_REGISTRY.get(extractor_name))
        if not extractor_class:
            raise ComponentNotFoundError(
                f"Extractor `{extractor_name}` not found please specify one of the: {list(EXTRACTOR_REGISTRY.keys())}"
            )

        click.echo(f"Loading and initializing loader: {loader_name}")
        loader_class = self.import_cls(LOADER_REGISTRY.get(loader_name))
        if not loader_class:
            raise ComponentNotFoundError(
                f"Loader `{loader_name}` not found please specify one of the following: {list(LOADER_REGISTRY.keys())}"
            )

        click.echo("Starting extraction ... ")
        results = set()
        extractor = extractor_class()
        for entity_name in extractor.entities:
            loader = loader_class(extractor=extractor, entity_name=entity_name)

            click.echo(f"Applying the schema for Entity {entity_name}")
            loader.schema_apply()

            click.echo(f"Extracting data for {entity_name}")
            entity_dfs = extractor.extract(entity_name)
            for df in entity_dfs:
                # click.echo("Got extractor results, loading them into the loader")
                results.add(loader.load(df=df))
        click.echo("Load done! Returning results ")
        return results
