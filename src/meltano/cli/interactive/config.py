"""Interactive configuration handler."""
import json
import textwrap

import click

from meltano.cli.interactive.utils import InteractionStatus
from meltano.cli.utils import CliError
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError


class InteractiveConfig:
    """Manage Config interactively."""

    def __init__(self, ctx, store, max_width=None):
        """Initialise InteractiveConfig instance."""
        self.ctx = ctx
        self.store = SettingValueStore(store)

        self.project = self.ctx.obj["project"]
        self.settings = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]

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
            current_value = (
                config_metadata.get("unexpanded_value") or config_metadata["value"]
            )
            current_value = "" if current_value is None else str(current_value)
            if len(current_value) > self.max_width:
                current_value = f"{current_value[: self.max_width]}..."
            setting_choices.append((str(index + 1), name, current_value))
        return setting_choices

    def _print_home_screen(self):
        """Print screen for this interactive."""
        if self.project.active_environment:
            click.echo(
                textwrap.dedent(
                    f"""
                    You are now configuring {self.settings.label.capitalize()} in Environment '{self.project.active_environment.name}'.
                    For help, please refer to plugin documentation: https://...
                    """
                )  # noqa: WPS355
            )
        else:
            click.echo(
                textwrap.dedent(
                    f"""
                    You are now configuring the base configuration of {self.settings.label.capitalize()} (i.e. without an Environment).
                    For help, please refer to plugin documentation: https://...
                    """
                )  # noqa: WPS355
            )
        indentation = "  "
        current_setting_values = "Current Setting Values"
        separator = "-" * len(current_setting_values)
        click.echo(separator)
        click.echo(current_setting_values)
        click.echo(separator)
        click.echo()
        for index, name, current_value in self.setting_choices:
            click.echo(f"{indentation}{index}) ", nl=False)
            click.secho(f"{name}: ", nl=False, fg="blue")
            click.secho(f"{current_value}", fg="green")

    def configure(self, setting_name, index=None, last_index=None):
        """Configure a single setting interactively."""
        current_value, config_metadata = self.settings.get_with_metadata(
            name=setting_name
        )

        if index and last_index:
            title = (
                f"{self.settings.label.capitalize()} setting {index} of {last_index}"
            )
        else:
            title = f"{self.settings.label.capitalize()} setting '{setting_name}'"
        separator = "-" * len(title)
        indentation = "  "

        click.echo()
        click.echo(separator)
        click.echo(title)
        click.echo(separator)
        click.echo()

        click.echo(f"{indentation}Setting name: ", nl=False)
        click.secho(f"{setting_name}", fg="blue", nl=True)

        setting_def = config_metadata["setting"]
        if setting_def.description:
            click.echo(f"{indentation}Description: {setting_def.description}")
        if setting_def.kind:
            click.echo(f"{indentation}Kind: {setting_def.kind}")

        default_value = getattr(setting_def, "value", None)
        if default_value is not None:
            click.echo(f"{indentation}Default: {default_value}")

        source = config_metadata["source"]
        if source is SettingValueStore.DEFAULT:
            label = "from default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{self.settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"

        current_unexpanded_value = config_metadata.get("unexpanded_value")
        if current_unexpanded_value:
            click.echo(f"{indentation}Current unexpanded value: ", nl=False)
            click.secho(f"{current_unexpanded_value}", fg="green", nl=True)
            if current_value != "":
                click.echo(
                    f"{indentation}Current expanded value ({label}): {current_value}"
                )
        else:
            if current_value != "":  # noqa: WPS513
                click.echo(f"{indentation}Current Value ({label}): ", nl=False)
                click.secho(f"{current_value}", fg="green", nl=True)

        click.echo()
        set_unset = click.prompt(
            "Do you want to set or unset this setting?",
            type=click.Choice(["set", "unset", "skip", "exit"], case_sensitive=False),
            default="skip" if default_value else "set",
        )
        if set_unset == "set":
            click.echo()
            new_value = click.prompt(
                "New value (enter to skip)", default="", show_default=False
            )
            click.echo()
            self.set_value(
                setting_name=tuple(setting_name.split(".")),
                value=new_value,
            )
        elif set_unset == "unset":
            self.unset_value(setting_name=tuple(setting_name.split(".")))
        elif set_unset == "skip":
            return InteractionStatus.SKIP
        elif set_unset == "exit":
            return InteractionStatus.EXIT

        click.echo()
        if not click.confirm("Done modifying this setting?", default=True):
            # TODO: this doesn't work as expected as config_metadata is cached (i.e. old values appear)
            # Need to refetch data at this point before calling configure_interactive again
            self.configure(setting_name, index, last_index)

    def configure_all(self):
        """Configure all settings."""
        while True:
            self._print_home_screen()

            click.echo()
            branch = click.prompt(
                "Would you like to configure a specific setting, or loop through all settings?",
                type=click.Choice(["select", "all", "exit"], case_sensitive=False),
                default="select",
            )
            if branch == "all":
                for index, name, _ in self.setting_choices:
                    status = self.configure(
                        setting_name=name,
                        index=index,
                        last_index=len(self.setting_choices),
                    )
                    if status == InteractionStatus.EXIT:
                        self.configure_all()

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
                status = self.configure(
                    setting_name=choice_name,
                    index=setting_index,
                    last_index=len(self.setting_choices),
                )
            elif branch == "exit":
                click.echo()
                break

    def set_value(self, setting_name, value):
        """Set value helper function."""
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        path = list(setting_name)
        try:
            value, metadata = self.settings.set_with_metadata(
                path, value, store=self.store, session=self.session
            )
        except StoreNotSupportedError as err:
            raise CliError(
                f"{self.settings.label.capitalize()} setting '{path}' could not be set in {self.store.label}: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        click.secho(
            f"{self.settings.label.capitalize()} setting '{name}' was set in {self.store.label}: {value!r}",
            fg="green",
        )

        current_value, source = self.settings.get_with_source(
            name, session=self.session
        )
        if source != store:
            click.secho(
                f"Current value is still: {current_value!r} (from {source.label})",
                fg="yellow",
            )

    def unset_value(self, setting_name):
        """Unset value helper."""
        path = list(setting_name)
        try:
            metadata = self.settings.unset(path, store=self.store, session=self.session)
        except StoreNotSupportedError as err:
            raise CliError(
                f"{self.settings.label.capitalize()} setting '{path}' in {self.store.label} could not be unset: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        click.secho(
            f"{self.settings.label.capitalize()} setting '{name}' in {store.label} was unset",
            fg="green",
        )

        current_value, source = self.settings.get_with_source(
            name, session=self.session
        )
        if source is not SettingValueStore.DEFAULT:
            click.secho(
                f"Current value is now: {current_value!r} (from {source.label})",
                fg="yellow",
            )
