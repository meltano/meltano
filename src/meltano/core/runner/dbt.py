import asyncio
import logging
from io import StringIO

from . import Runner
from meltano.core.error import SubprocessError
from meltano.core.project import Project
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.connection_service import ConnectionService
from meltano.core.dbt_service import DbtService
from meltano.core.config_service import ConfigService
from meltano.core.db import project_engine
from meltano.core.elt_context import ELTContext


class DbtRunner(Runner):
    def __init__(self, elt_context: ELTContext, dbt_service: DbtService = None):
        self.context = elt_context
        self.dbt_service = dbt_service or DbtService(elt_context.project)
        self.connection_service = ConnectionService(elt_context)

    @property
    def project(self):
        return self.context.project

    def run(self, session, dry_run=False, models=None):
        # we should probably refactor this part to have an ELTContext object already
        # filled with the each plugins' configuration so we don't have to query
        # multiple times for the same data.

        settings_service = PluginSettingsService(self.project)
        try:
            load = self.connection_service.load_params()
            analyze = self.connection_service.analyze_params()
            env = {
                # inject the inferred 'schemas' from the ELTContext
                "MELTANO_LOAD_SCHEMA": load["schema"],
                "MELTANO_ANALYZE_SCHEMA": analyze["schema"],
                "DBT_TARGET": self.connection_service.dialect,
                # inject the extractor & loader configuration as ENV variables.
                # that means dbt will have access to all the configuration of
                # the extractor and loader
                **settings_service.as_env(session, self.context.extractor.ref),
                **settings_service.as_env(session, self.context.loader.ref),
            }
        except Exception as e:
            logging.debug("Could not inject environment to dbt.")
            logging.debug(f"Could not hydrate ENV from the EltContext: {str(e)}")
            raise e

        # Get an asyncio event loop and use it to run the dbt commands
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dbt_service.clean())
        loop.run_until_complete(self.dbt_service.deps())

        if models is not None:
            models = models.replace("-", "_")

        if dry_run:
            loop.run_until_complete(self.dbt_service.compile(models, env=env))
        else:
            loop.run_until_complete(self.dbt_service.run(models, env=env))
