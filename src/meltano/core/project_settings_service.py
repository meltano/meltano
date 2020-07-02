from meltano.core.settings_service import SettingsService


class ProjectSettingsService(SettingsService):
    config_override = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.env_override = {**self.project.env, **self.env_override}

        self.config_override = {
            **self.__class__.config_override,
            **self.config_override,
        }

    @property
    def _env_namespace(self):
        return "meltano"

    @property
    def _db_namespace(self):
        return "meltano"

    @property
    def _definitions(self):
        return self.config_service.settings

    @property
    def _meltano_yml_config(self):
        return self.config_service.current_config

    def _update_meltano_yml_config(self):
        self.config_service.update_config()
