"""Interactive configuration handler."""
import json
import textwrap

import click

from meltano.cli.interactive.utils import InteractionStatus
from meltano.cli.utils import CliError
from meltano.core.environment_service import EnvironmentService
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError

PLUGIN_COLOUR = "magenta"
ENVIRONMENT_COLOUR = "yellow"


class InteractiveConfig:  # noqa: WPS230, WPS214
    """Manage Config interactively."""

    def __init__(self, ctx, store, extras=False, max_width=None):
        """Initialise InteractiveConfig instance."""
        self.ctx = ctx
        self.store = store
        self.extras = extras
        self.project = self.ctx.obj["project"]
        self.settings = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]
        self.plugin = self.ctx.obj["settings"].plugin
        self.environment_service = EnvironmentService(self.project)
        self.max_width = max_width or 80  # noqa: WPS432
        self.indentation = "  "

    @property
    def configurable_settings(self):
        """Return settings available for interactive configuration."""
        return self.settings.config_with_metadata(
            session=self.session, extras=self.extras
        )

    @property
    def setting_choices(self):
        """Return simplified setting choices, for easy printing."""
        setting_choices = []
        for index, (name, config_metadata) in enumerate(
            self.configurable_settings.items()
        ):
            description = config_metadata["setting"].description
            description = "" if description is None else description
            setting_choices.append((str(index + 1), name, description))
        return setting_choices

    @property
    def environment_label(self):
        """Format the current Environment for presentation."""
        if self.project.active_environment:
            return f"Environment '{self.project.active_environment.name}'"
        return "Base (i.e. no Environment)"

    def wrap(self, text: str, indentation: str = "") -> str:
        """Wrap text to maximum width."""
        return f"\n{indentation}".join(textwrap.wrap(text, width=self.max_width))

    def truncate(self, text: str) -> str:
        """Truncate text."""
        return f"{text[: self.max_width - 3]}..."

    def _print_home_title(self):
        """Print title text."""
        environment_name = None
        if self.project.active_environment:
            environment_name = self.project.active_environment.name

        if environment_name:
            title = f"Configuring {self.settings.label.capitalize()} in Environment '{environment_name}' interactively."
            separator = "-" * len(title)
        else:
            title = f"Configuring {self.settings.label.capitalize()} interactively."
            separator = "-" * len(title)

        click.echo()
        click.echo(separator)
        click.echo("Configuring", nl=False)
        click.secho(f" {self.settings.label.capitalize()}", nl=False, fg=PLUGIN_COLOUR)
        if environment_name:
            click.echo(" in Environment ", nl=False)
            click.secho(f"'{environment_name}'", fg="green", nl=False)
        click.echo(" interactively.")
        click.echo(separator)

    def _print_home_help(self):
        """Print help text."""
        click.echo()
        click.echo(
            f"{self.indentation}By following the prompts below, you will be guided through configuration of this plugin."
        )
        click.echo()
        click.echo(
            f"{self.indentation}Meltano is responsible for managing the configuration of all of a project’s plugins."
        )
        click.echo(
            f"{self.indentation}It knows what settings are supported by each plugin, and how and when different"
        )
        click.echo(
            f"{self.indentation}types of plugins expect to be fed that configuration."
        )
        click.echo()
        click.echo(
            f"{self.indentation}To determine the values of settings, Meltano will look in 4 main places,"
        )
        click.echo(f"{self.indentation}with each taking precedence over the next:")
        click.echo()
        click.echo(f"{self.indentation*2}1) Environment variables")
        click.echo(f"{self.indentation*2}2) Your meltano.yml project file")
        click.echo(f"{self.indentation*2}3) Your project's system database")
        click.echo(
            f"{self.indentation*2}4) The default values set in the plugin's settings metadata"
        )
        click.echo()
        click.echo(
            f"{self.indentation}Within meltano.yml (2) you can also associate configuration with a Meltano Environment,"
        )
        click.echo(
            f"{self.indentation}allowing you to define custom layers of configuration within your project."
        )
        click.echo()
        click.echo(
            f"{self.indentation}You will be asked where you would like to store setting values, and optionally which Environment to use."
        )

    def _print_home_available_settings(self):
        """Print available setting names and current values."""
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
            click.echo(f"{self.indentation}{index}) ", nl=False)
            click.secho(f"{name}", nl=False, fg="blue")
            if description:
                click.secho(f": {self.truncate(description)}")
            else:
                click.echo()

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
            title += subtitle
        separator_width = len(title)
        separator = "-" * separator_width

        click.echo()
        click.echo(separator)
        click.secho(f"{self.settings.label.capitalize()}", nl=False, fg=PLUGIN_COLOUR)
        click.echo(f" (Setting {index} of {last_index})")
        click.echo(separator)
        return separator

    def _print_setting(self, name, config_metadata):
        """Print setting."""
        value = config_metadata["value"]
        source = config_metadata["source"]
        setting_def = config_metadata["setting"]

        if setting_def.description:
            click.echo()
            click.echo(
                f"{self.indentation}{self.wrap(setting_def.description, indentation=self.indentation)}"
            )

        if setting_def.is_extra:
            click.echo()
            click.secho(
                f"{self.indentation}Custom Extra: plugin-specific options handled by Meltano",
                fg="yellow",
            )
        elif setting_def.is_custom:
            click.echo()
            click.secho(
                f"{self.indentation}Custom Setting: possibly unsupported by the plugin",
                fg="yellow",
            )

        click.echo()
        click.echo(f"{self.indentation}Name: ", nl=False)
        click.secho(f"{name}", fg="blue")

        kind = setting_def.kind
        if kind:
            click.echo(f"{self.indentation}Kind: {kind}")

        env_keys = [
            var.definition for var in self.settings.setting_env_vars(setting_def)
        ]
        click.echo(f"{self.indentation}Env: {', '.join(env_keys)}")

        if source is not SettingValueStore.DEFAULT:
            default_value = setting_def.value
            if default_value is not None:
                click.echo(f"{self.indentation}Default: {default_value!r}")

        if source is SettingValueStore.DEFAULT:
            label = "default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{self.settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"

        expanded_value = value
        unexpanded_value = config_metadata.get("unexpanded_value")
        if unexpanded_value:
            current_value = click.style(f"{unexpanded_value!r}", fg="green")
            click.echo(f"{self.indentation}Current Expanded Value: '{expanded_value}'")
        else:
            current_value = click.style(f"{value!r}", fg="green")
        click.echo(f"{self.indentation}Current Value ({label}): {current_value}")

        docs_url = self.settings.docs_url
        if docs_url:
            click.echo()
            click.echo(
                self.wrap(
                    f"{self.indentation}To learn more about {self.settings.label} and its settings, visit {docs_url}",
                    indentation=self.indentation,
                )
            )

    def configure(self, name, index=None, last_index=None):
        """Configure a single setting interactively."""
        config_metadata = next(
            (
                config_metadata
                for nme, config_metadata in self.configurable_settings.items()
                if nme == name
            )
        )
        separator = self._print_setting_title(index=index, last_index=last_index)
        self._print_setting(name=name, config_metadata=config_metadata)
        click.echo()
        click.echo(separator)
        click.echo()

        set_unset = click.prompt(
            "Set, unset, skip or exit this setting?",
            type=click.Choice(["set", "unset", "skip", "exit"], case_sensitive=False),
            default="skip",
        )
        if set_unset == "set":
            click.echo()
            new_value = click.prompt(
                "New value (enter to skip)", default="", show_default=False
            )
            click.echo()
            self.set_value(
                setting_name=tuple(name.split(".")),
                value=new_value,
                store=self.store,
            )
            click.echo()
            click.pause()
        elif set_unset == "unset":
            click.echo()
            self.unset_value(setting_name=tuple(name.split(".")), store=self.store)
            click.echo()
            click.pause()
        elif set_unset == "skip":
            return InteractionStatus.SKIP
        elif set_unset == "exit":
            return InteractionStatus.EXIT

    def configure_all(self):
        """Configure all settings."""
        while True:
            click.clear()
            self._print_home_screen()

            click.echo()
            branch = click.prompt(
                "Select a specific setting, loop through all settings or exit?",
                type=click.Choice(["select", "all", "exit"], case_sensitive=False),
                default="all",
            )
            if branch == "all":
                for index, name, _ in self.setting_choices:
                    status = InteractionStatus.START
                    while status not in {
                        InteractionStatus.SKIP,
                        InteractionStatus.EXIT,
                    }:
                        click.clear()
                        status = self.configure(
                            name=name, index=index, last_index=len(self.setting_choices)
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
                    name=choice_name,
                    index=setting_index,
                    last_index=len(self.setting_choices),
                )
            elif branch == "exit":
                click.echo()
                break

    def set_value(self, setting_name, value, store):
        """Set value helper function."""
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        settings = self.settings
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

    def unset_value(self, setting_name, store):
        """Unset value helper."""
        settings = self.settings
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
