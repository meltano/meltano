import logging
import subprocess
from io import StringIO

from . import Runner
from meltano.core.project import Project
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.dbt_service import DbtService
from meltano.core.config_service import ConfigService
from meltano.core.db import project_engine


class DbtRunner(Runner):
    def __init__(
        self,
        project: Project,
        config_service: ConfigService = None,
        dbt_service: DbtService = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.dbt_service = dbt_service or DbtService(project)

    def run(self, extractor: str, loader: str, dry_run=False, models=None):
        extractor = self.config_service.get_plugin(
            extractor, plugin_type=PluginType.EXTRACTORS
        )
        loader = self.config_service.get_plugin(loader, plugin_type=PluginType.LOADERS)

        # we should probably refactor this part to have an ELTContext object already
        # filled with the each plugins' configuration so we don't have to query
        # multiple times for the same data.
        _, Session = project_engine(self.project)

        session = Session()
        try:
            extractor_settings = PluginSettingsService(session, self.project, extractor)
            loader_settings = PluginSettingsService(session, self.project, loader)

            # send the elt_context as ENV variables
            env = {**extractor_settings.as_env(), **loader_settings.as_env()}
        except Exception as e:
            logging.warning("Could not inject environment to dbt.")
            logging.debug("Could not hydrate ENV from the EltContext: {str(e)}")

        self.dbt_service.deps()

        if models is not None:
            models = models.replace("-", "_")

        if dry_run:
            self.dbt_service.compile(models, env=env)
        else:
            self.dbt_service.run(models, env=env)
