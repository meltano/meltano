"""Interactive configuration handler."""
import json
import textwrap

import click

from meltano.cli.interactive.utils import InteractionStatus
from meltano.cli.utils import CliError
from meltano.core.environment_service import EnvironmentService
from meltano.core.plugin import settings_service
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError

PLUGIN_COLOUR = "magenta"
ENVIRONMENT_COLOUR = "yellow"


class InteractiveConfig:
    """Manage Config interactively."""

    def __init__(self, ctx, max_width=None):
        """Initialise InteractiveConfig instance."""
        self.ctx = ctx
        self.auto_store_manager = SettingValueStore("auto").manager
        self.project = self.ctx.obj["project"]
        self.settings = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]
        self.plugin = self.ctx.obj["settings"].plugin
        self.environment_service = EnvironmentService(self.project)
        self.max_width = max_width or 77  # noqa: WPS432

    @property
    def configurable_settings(self):
        """Return settings available for interactive configuration."""
        full_config = self.settings.config_with_metadata(session=self.session)
        return {key: value for key, value in full_config.items() if key != "_settings"}

    @property
    def setting_choices(self):
        """Return simplified setting choices, for easy printing."""
        setting_choices = []
        for index, (name, config_metadata) in enumerate(
            self.configurable_settings.items()
        ):
            description = config_metadata["setting"].description
            description = "" if description is None else description
            if len(description) > self.max_width:
                description = f"{description[: self.max_width]}..."
            setting_choices.append((str(index + 1), name, description))
        return setting_choices

    @property
    def environment_label(self):
        """Format the current Environment for presentation."""
        if self.project.active_environment:
            return f"Environment '{self.project.active_environment.name}'"
        return "Base (i.e. no Environment)"

    def _print_home_title(self):
        """Print title text."""
        title = f"Configuring {self.settings.label.capitalize()} interactively."
        separator = "-" * len(title)

        click.echo()
        click.echo(separator)
        click.echo("Configuring", nl=False)
        click.secho(f" {self.settings.label.capitalize()}", nl=False, fg=PLUGIN_COLOUR)
        click.echo(" interactively.")
        click.echo(separator)

    def _print_home_help(self):
        """Print help text."""
        indentation = "  "
        click.echo()
        click.echo(
            f"{indentation}By following the prompts below, you will be guided through configuration of this plugin."
        )
        click.echo()
        click.echo(
            f"{indentation}Meltano is responsible for managing the configuration of all of a project’s plugins."
        )
        click.echo(
            f"{indentation}It knows what settings are supported by each plugin, and how and when different"
        )
        click.echo(
            f"{indentation}types of plugins expect to be fed that configuration."
        )
        click.echo()
        click.echo(
            f"{indentation}To determine the values of settings, Meltano will look in 4 main places,"
        )
        click.echo(f"{indentation}with each taking precedence over the next:")
        click.echo()
        click.echo(f"{indentation*2}1) Environment variables")
        click.echo(f"{indentation*2}2) Your meltano.yml project file")
        click.echo(f"{indentation*2}3) Your project's system database")
        click.echo(
            f"{indentation*2}4) The default values set in the plugin's settings metadata"
        )
        click.echo()
        click.echo(
            f"{indentation}Within meltano.yml (2) you can also associate configuration with a Meltano Environment,"
        )
        click.echo(
            f"{indentation}allowing you to define custom layers of configuration within your project."
        )
        click.echo()
        click.echo(
            f"{indentation}You will be asked where you would like to store setting values, and optionally which Environment to use."
        )

    def _print_home_available_settings(self):
        """Print available setting names and current values."""
        indentation = "  "
        title = f"Available '{self.settings.plugin.name}' Settings"
        separator = "-" * len(title)
        click.echo()
        click.echo(separator)
        click.echo("Available ", nl=False)
        click.secho(f"'{self.settings.plugin.name}'", nl=False, fg=PLUGIN_COLOUR)
        click.echo(" Settings")
        click.echo(separator)
        click.echo()
        for index, name, description in self.setting_choices:
            click.echo(f"{indentation}{index}) ", nl=False)
            click.secho(f"{name}: ", nl=False, fg="green")
            click.secho(f"{description}")

    def _print_home_screen(self):
        """Print screen for this interactive."""
        self._print_home_title()
        self._print_home_help()
        self._print_home_available_settings()

    def _print_setting_title(self, index, last_index):
        """Print setting title."""
        title = f"{self.settings.label.capitalize()}"
        subtitle = ""
        if index and last_index:
            subtitle = f" (Setting {index} of {last_index})"
            title = title + subtitle
        separator_width = len(title)
        separator = "-" * separator_width

        click.echo()
        click.echo(separator)
        click.secho(f"{self.settings.label.capitalize()}", nl=False, fg=PLUGIN_COLOUR)
        click.echo(f" (Setting {index} of {last_index})")
        click.echo(separator)

    def _get_value_from_store(
        self, setting_service, setting_name, store, environment_name=None
    ):
        """Get setting value."""
        try:
            value = setting_service.get(setting_name, source=store)
            if value:
                return (value, store, environment_name)
        except StoreNotSupportedError:
            pass

    def _get_settable_values(self, setting_name):
        supported_stores = [
            SettingValueStore.MELTANO_ENV,
            SettingValueStore.MELTANO_YML,
            SettingValueStore.DOTENV,
            SettingValueStore.DB,
        ]
        settable_values = []
        for store in supported_stores:
            if store == SettingValueStore.MELTANO_ENV:
                active_environment_name = self.project.active_environment.name
                try:
                    for environment in self.environment_service.list_environments():
                        self.project.activate_environment(environment.name)
                        settings = PluginSettingsService(
                            project=self.project,
                            plugin=self.settings.plugin,
                            plugins_service=self.settings.plugins_service,
                        )
                        settable_value = self._get_value_from_store(
                            setting_service=settings,
                            setting_name=setting_name,
                            store=store,
                            environment_name=environment.name,
                        )
                        if settable_value:
                            settable_values.append(settable_value)
                finally:
                    self.project.activate_environment(active_environment_name)
            else:
                settable_value = self._get_value_from_store(
                    setting_service=self.settings,
                    setting_name=setting_name,
                    store=store,
                )
                if settable_value:
                    settable_values.append(settable_value)
        return settable_values

    def _print_setting_values(self, setting_name, indentation):
        settable_values = self._get_settable_values(setting_name=setting_name)

        if settable_values:
            click.echo()
            click.echo(f"{indentation}Values:")
            for value, store, environment_name in settable_values:
                if store == SettingValueStore.MELTANO_ENV:
                    click.echo(
                        f"{indentation}  {store.label} ({environment_name}): {value}"
                    )
                else:
                    click.echo(f"{indentation}  {store.label}: {value}")
        else:
            click.echo(f"{indentation}Value: (none)")

    def _print_setting(self, setting_name):
        """Print setting."""
        current_value, config_metadata = self.settings.get_with_metadata(
            name=setting_name
        )

        indentation = "  "
        click.echo()
        click.echo(f"{indentation}Name: ", nl=False)
        click.secho(f"{setting_name}", fg="blue", nl=True)

        setting_def = config_metadata["setting"]
        if setting_def.description:
            click.echo(f"{indentation}Description: {setting_def.description}")
        if setting_def.kind:
            click.echo(f"{indentation}Kind: {setting_def.kind}")

        default_value = getattr(setting_def, "value", None)
        if default_value is not None:
            click.echo(f"{indentation}Default: {default_value}")

        self._print_setting_values(setting_name=setting_name, indentation=indentation)

    def _prompt_select_store(self):
        """Choose a Store for this setting."""
        click.echo()
        choices = [
            ("1", "meltano environment in meltano.yml", SettingValueStore.MELTANO_ENV),
            ("2", "base meltano.yml (no environment)", SettingValueStore.MELTANO_YML),
            ("3", ".env file", SettingValueStore.DOTENV),
            ("4", "system database", SettingValueStore.DB),
            ("5", "auto", SettingValueStore.AUTO),
        ]
        indentation = "  "
        for choice in choices:
            click.echo(f"{indentation}{choice[0]}) {choice[1]}")

        click.echo()
        chosen = click.prompt(
            "Select store for new value",
            type=click.Choice([chs[0] for chs in choices]),
            default="1",
        )
        return next(chs[2] for chs in choices if chs[0] == chosen)

    def _prompt_select_environment(self):
        """Choose an Environment for this setting."""
        environments = {
            env.name: env for env in self.environment_service.list_environments()
        }
        choices = {
            str(index + 1): env_name
            for index, env_name in enumerate(environments.keys())
        }
        choice_keys = {value: key for key, value in choices.items()}
        click.echo()
        indentation = "  "
        for index, choice in choices.items():
            click.echo(f"{indentation}{index}) {choice}")
        click.echo()
        chosen = click.prompt(
            "Select Environment for new value",
            type=click.Choice(choices.keys()),
            default=choice_keys[self.project.active_environment.name],
        )
        return environments[choices[chosen]]

    def configure(self, setting_name, index=None, last_index=None):
        """Configure a single setting interactively."""
        self._print_setting_title(index=index, last_index=last_index)
        self._print_setting(setting_name=setting_name)

        click.echo()
        set_unset = click.prompt(
            "Set, unset, skip or exit this setting?",
            type=click.Choice(["set", "unset", "skip", "exit"], case_sensitive=False),
            default="skip",
        )
        if set_unset == "set":
            store = self._prompt_select_store()
            environment = None
            if store == SettingValueStore.MELTANO_ENV:
                environment = self._prompt_select_environment()

            click.echo()
            new_value = click.prompt(
                "New value (enter to skip)", default="", show_default=False
            )
            click.echo()
            self.set_value(
                setting_name=tuple(setting_name.split(".")),
                value=new_value,
                store=store,
                environment=environment,
            )
        elif set_unset == "unset":
            store = self._prompt_select_store()
            environment = None
            if store == SettingValueStore.MELTANO_ENV:
                environment = self._prompt_select_environment()
            self.unset_value(
                setting_name=tuple(setting_name.split(".")),
                store=store,
                environment=environment,
            )
        elif set_unset == "skip":
            return InteractionStatus.SKIP
        elif set_unset == "exit":
            return InteractionStatus.EXIT

        click.echo()
        if not click.confirm("Done modifying this setting?", default=True):
            self.configure(setting_name, index, last_index)

    def configure_all(self):
        """Configure all settings."""
        while True:
            click.clear()
            self._print_home_screen()

            click.echo()
            branch = click.prompt(
                "Select a specific setting, loop through all settings or exit?",
                type=click.Choice(["select", "all", "exit"], case_sensitive=False),
                default="select",
            )
            if branch == "all":
                for index, name, _ in self.setting_choices:
                    click.clear()
                    status = self.configure(
                        setting_name=name,
                        index=index,
                        last_index=len(self.setting_choices),
                    )
                    if status == InteractionStatus.EXIT:
                        click.clear()
                        break

            elif branch == "select":
                choice_numbers = [idx for idx, _, _ in self.setting_choices]
                setting_index = click.prompt(
                    "Setting number", type=click.Choice(choice_numbers)
                )
                choice_name = next(
                    (
                        nme
                        for idx, nme, _ in self.setting_choices
                        if idx == setting_index
                    )
                )
                click.clear()
                status = self.configure(
                    setting_name=choice_name,
                    index=setting_index,
                    last_index=len(self.setting_choices),
                )
            elif branch == "exit":
                click.echo()
                break

    def set_value(self, setting_name, value, store, environment=None):
        """Set value helper function."""
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        settings = self.settings
        if environment and store == SettingValueStore.MELTANO_ENV:
            self.project.activate_environment(environment.name)
            settings = PluginSettingsService(
                project=self.project,
                plugin=self.settings.plugin,
                plugins_service=self.settings.plugins_service,
            )

        path = list(setting_name)
        try:
            value, metadata = settings.set_with_metadata(
                path, value, store=store, session=self.session
            )
        except StoreNotSupportedError as err:
            raise CliError(
                f"{settings.label.capitalize()} setting '{path}' could not be set in {store.label}: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        click.secho(
            f"{settings.label.capitalize()} setting '{name}' was set in {store.label}: {value!r}",
            fg="green",
        )

        current_value, source = settings.get_with_source(name, session=self.session)
        if source != store:
            click.secho(
                f"Current value is still: {current_value!r} (from {source.label})",
                fg="yellow",
            )

    def unset_value(self, setting_name, store, environment=None):
        """Unset value helper."""
        settings = self.settings
        if environment and store == SettingValueStore.MELTANO_ENV:
            self.project.activate_environment(environment.name)
            settings = PluginSettingsService(
                project=self.project,
                plugin=self.settings.plugin,
                plugins_service=self.settings.plugins_service,
            )

        path = list(setting_name)
        try:
            metadata = settings.unset(path, store=store, session=self.session)
        except StoreNotSupportedError as err:
            raise CliError(
                f"{settings.label.capitalize()} setting '{path}' in {store.label} could not be unset: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        click.secho(
            f"{settings.label.capitalize()} setting '{name}' in {store.label} was unset",
            fg="green",
        )

        current_value, source = settings.get_with_source(name, session=self.session)
        if source is not SettingValueStore.DEFAULT:
            click.secho(
                f"Current value is now: {current_value!r} (from {source.label})",
                fg="yellow",
            )
