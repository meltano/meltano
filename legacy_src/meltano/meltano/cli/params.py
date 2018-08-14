import click
import os

from meltano.common.manifest_reader import ManifestReader


class ManifestParamType(click.ParamType):
    name = 'manifest'

    def convert(self, value, param, ctx):
        source_name, _ = os.path.basename(value).split(".")
        reader = ManifestReader(source_name)
        try:
            with open(value, 'r') as file:
                return reader.load(file)
        except IOError:
            self.fail('cannot open %s.' % value, param, ctx)


MANIFEST_TYPE = ManifestParamType()
