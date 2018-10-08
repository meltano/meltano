import importlib
import click

from . import Runner


# TODO: to be generated from the file structure of /Extract/
EXTRACTOR_REGISTRY = {
    'fastly': ("extract.fastly", "FastlyExtractor"),
    'demo': ("extract.demo", "DemoExtractor"),
    'sfdc': ("extract.sfdc.extractor", "SfdcExtractor"),
}

LOADER_REGISTRY = {
    'postgres': ("load.postgres.loader", "PostgresLoader"),
    'csv': ("load.csv.loader", "CsvLoader"),
    'snowflake': ("load.csv.loader", "SnowflakeLoader"),
}


class MeltanoRunner(Runner):
    def import_cls(registry):
        mod_name, cls_name = registry
        mod = importlib.import_module(mod_name)
        return getattr(mod, cls_name)

    def run(self,
            extractor_name,
            loader_name):
        click.echo(f"Loading and initializing extractor: {extractor_name}")
        extractor_class = self.import_cls(EXTRACTOR_REGISTRY.get(extractor_name))
        if not extractor_class:
            raise Exception(
                f'Extractor {extractor_name} not found please specify one of the: {list(EXTRACTOR_REGISTRY.keys())}'
            )

        click.echo(f"Loading and initializing loader: {loader_name}")
        loader_class = self.import_cls(LOADER_REGISTRY.get(loader_name))
        if not loader_class:
            raise Exception(
                f'Loader {loader_name} not found please specify one of the following: {list(LOADER_REGISTRY.keys())}'
            )

        click.echo("Starting extraction ... ")
        results = set()
        extractor = extractor_class()
        for entity_name in extractor.entities:
            loader = loader_class(
                extractor=extractor,
                entity_name=entity_name,
            )

            click.echo(f'Applying the schema for Entity {entity_name}')
            loader.schema_apply()

            click.echo(f'Extracting data for {entity_name}')
            entity_dfs = extractor.extract(entity_name)
            for df in entity_dfs:
                # click.echo("Got extractor results, loading them into the loader")
                results.add(loader.load(df=df))
        click.echo("Load done! Returning results ")
        return results
