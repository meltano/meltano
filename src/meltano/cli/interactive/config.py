"""Interactive configuration handler."""

from __future__ import annotations

import typing as t
from contextlib import suppress

# NOTE: Importing the readline module enables the use of arrow
#       keys for text navigation during interactive config.
#       Refer to https://docs.python.org/3/library/readline.html
with suppress(ImportError):
    import readline  # noqa: F401

import click
from jinja2 import BaseLoader, Environment
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from meltano.cli.interactive.utils import InteractionStatus
from meltano.core.environment_service import EnvironmentService
from meltano.core.settings_service import (
    REDACTED_VALUE,
    SettingKind,
    SettingsService,
    SettingValueStore,
)
from meltano.core.settings_store import StoreNotSupportedError
from meltano.core.tracking.contexts import CliEvent

if t.TYPE_CHECKING:
    from meltano.core.project import Project

PLUGIN_COLOR = "magenta"
ENVIRONMENT_COLOR = "orange1"
SETTING_COLOR = "blue1"

HOME_SCREEN_TEMPLATE = """[bold underline]Configuring [{{ plugin_color }}]{{ plugin_name.capitalize() | safe }}[/{{ plugin_color }}] {% if environment_name %}in Environment [{{ environment_color }}]{{ environment_name }}[/{{ environment_color }}] {% endif %}Interactively[/bold underline]

Following the prompts below, you will be guided through configuration of this plugin.

Meltano is responsible for managing the configuration of all of a project's plugins.
It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

To determine the values of settings, Meltano will look in 4 main places, with each taking precedence over the next:

  1. Environment variables
  2. Your meltano.yml project file
  3. Your project's system database
  4. The default values set in the plugin's settings metadata

Within meltano.yml you can also associate configuration with a Meltano Environment, allowing you to define custom layers of configuration within your project.

To learn more about configuration options, see the [link=https://docs.meltano.com/guide/configuration]Meltano Configuration Guide[/link]

[bold underline]Settings[/bold underline]
{% for setting in settings %}
{{ loop.index }}. [blue]{{ setting["name"] }}[/blue]: {{ setting["description"] | safe }}
{%- endfor %}

{% if plugin_url %}To learn more about {{ plugin_name | safe }} and its settings, visit [link={{ plugin_url }}]{{ plugin_url }}[/link]{% endif %}
"""  # noqa: E501


class InteractiveConfig:
    """Manage Config interactively."""

    def __init__(self, ctx, store, *, extras=False, max_width=None) -> None:  # noqa: ANN001
        """Initialise InteractiveConfig instance."""
        self.ctx = ctx
        self.store = store
        self.extras = extras
        self.project: Project = self.ctx.obj["project"]
        self.settings: SettingsService = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]
        self.tracker = self.ctx.obj["tracker"]
        self.environment_service = EnvironmentService(self.project)
        self.max_width = max_width or 75
        self.console = Console()
        self.safe: bool = ctx.obj["safe"]

    @property
    def configurable_settings(self):  # noqa: ANN201
        """Return settings available for interactive configuration."""
        return self.settings.config_with_metadata(
            session=self.session,
            extras=self.extras,
            redacted=self.safe,
        )

    @property
    def setting_choices(self) -> list[tuple[str, str, str]]:
        """Return simplified setting choices, for easy printing."""
        setting_choices: list[tuple[str, str, str]] = []
        for index, (name, config_metadata) in enumerate(
            self.configurable_settings.items(),
        ):
            description = config_metadata["setting"].description
            description = "" if description is None else description
            setting_choices.append((str(index + 1), name, description))
        return setting_choices

    def truncate(self, text: str) -> str:
        """Truncate text."""
        if len(text) >= self.max_width:
            return f"{text[: self.max_width - 3]}..."
        return text

    def _print_home_screen(self) -> None:
        """Print screen for this interactive."""
        markdown_template = Environment(
            loader=BaseLoader(),
            autoescape=True,
        ).from_string(
            HOME_SCREEN_TEMPLATE,
        )
        markdown_text = markdown_template.render(
            {
                "plugin_color": PLUGIN_COLOR,
                "environment_color": ENVIRONMENT_COLOR,
                "setting_color": SETTING_COLOR,
                "plugin_name": self.settings.label,
                "plugin_url": self.settings.docs_url,
                "environment_name": self.project.environment.name
                if self.project.environment
                else None,
                "settings": [
                    {
                        "name": name,
                        "description": self.truncate(description.replace("\n", " ")),
                    }
                    for _, name, description in self.setting_choices
                ],
            },
        )
        self.console.print(Panel(Text.from_markup(markdown_text)))

    def _print_setting(self, name, config_metadata, index, last_index) -> None:  # noqa: ANN001
        """Print setting."""
        value = config_metadata["value"]
        source = config_metadata["source"]
        setting_def = config_metadata["setting"]
        details = Table(show_header=False)
        details.add_column("name", justify="right")
        details.add_column("value")

        pre = [
            Text.from_markup(
                f"[bold underline][{PLUGIN_COLOR}]"
                f"{self.settings.label.capitalize()}[/{PLUGIN_COLOR}]"
                f"[/bold underline] Setting {index} of {last_index}",
            ),
        ]

        if setting_def.is_extra:
            pre.append(
                Text.from_markup(
                    "[yellow1]Custom Extra: plugin-specific options handled "
                    "by Meltano[/yellow1]",
                ),
            )

        elif setting_def.is_custom:
            pre.append(
                Text.from_markup(
                    "[yellow1]Custom Setting: possibly unsupported by the "
                    "plugin[/yellow1]",
                ),
            )

        details.add_row(
            Text("Name"),
            Text.from_markup(f"[{SETTING_COLOR}]{name}[/{SETTING_COLOR}]"),
        )

        if source is SettingValueStore.DEFAULT:
            label = "default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{self.settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"

        def value_is_defined(v=value):  # noqa: ANN001, ANN202
            return v is not None

        def value_for_display(v=value):  # noqa: ANN001, ANN202
            return v if value_is_defined(v) else "(empty string)"

        expanded_value = value_for_display()
        unexpanded_value = config_metadata.get("unexpanded_value")

        if unexpanded_value:
            current_value = value_for_display(unexpanded_value)
            details.add_row(Text("Current expanded value"), Text(f"{expanded_value}"))
        else:
            current_value = expanded_value

        redacted_with_value = (
            self.safe and setting_def.is_redacted and value_is_defined()
        )
        value_color = "yellow" if redacted_with_value else "green"

        details.add_row(
            Text(f"Current value ({label})"),
            Text.from_markup(f"[{value_color}]{current_value}[/{value_color}]"),
        )

        if setting_def.kind:
            details.add_row(Text("Kind"), Text(f"{setting_def.kind}"))
        if source is not SettingValueStore.DEFAULT:
            default_value = setting_def.value
            if default_value is not None:
                details.add_row(Text("Default"), Text(f"{default_value!r}"))
        env_keys = [
            var.definition for var in self.settings.setting_env_vars(setting_def)
        ]

        details.add_row(Text("Env(s)"), Text(f"{', '.join(env_keys)}"))
        post = []
        if setting_def.description:
            post.append(
                Group(
                    Text(" Description:"),
                    Panel(Markdown(setting_def.description, justify="left")),
                ),
            )

        if docs_url := self.settings.docs_url:
            post.append(
                Text.from_markup(
                    f" To learn more about {self.settings.label} and its "
                    f"settings, visit [link={docs_url}]{docs_url}[/link]",
                ),
            )

        self.console.print(Panel(Group(*pre, details, *post)))

    @staticmethod
    def _value_prompt(config_metadata):  # noqa: ANN001, ANN205
        if config_metadata["setting"].kind != SettingKind.OPTIONS:
            return (
                click.prompt(
                    "New value (redacted)",
                    default="",
                    show_default=False,
                    hide_input=True,
                    confirmation_prompt=True,
                )
                if config_metadata["setting"].is_redacted
                else click.prompt("New value", default="", show_default=False)
            )

        options_index = {
            str(index + 1): value
            for index, value in enumerate(
                (chs["label"], chs["value"])
                for chs in config_metadata["setting"].options
            )
        }

        click.echo()
        for index, value in options_index.items():
            click.echo(f"{index}. {value[0]}")
        click.echo()
        chosen_index = click.prompt(
            "Select value",
            type=click.Choice(list(options_index.keys())),
            show_default=False,
        )
        return options_index[chosen_index][1]

    def configure(self, name, index=None, last_index=None, *, show_set_prompt=True):  # noqa: ANN001, ANN201
        """Configure a single setting interactively."""
        config_metadata = next(
            (
                config_metadata
                for nme, config_metadata in self.configurable_settings.items()
                if nme == name
            ),
        )
        self._print_setting(
            name=name,
            config_metadata=config_metadata,
            index=index,
            last_index=last_index,
        )

        action = "y"
        if show_set_prompt:
            try:
                click.echo()
                action = click.prompt(
                    "Set this value (Y/n) or exit (e)?",
                    default="y",
                    type=click.Choice(["y", "n", "e"], case_sensitive=False),
                )
            except click.Abort:
                action = "e"

        if action.lower() == "y":
            while True:
                click.echo()
                try:
                    new_value = self._value_prompt(config_metadata)
                except click.Abort:
                    click.echo()
                    click.echo("Skipping...")
                    click.pause()
                    return InteractionStatus.SKIP

                try:
                    click.echo()
                    self.set_value(
                        setting_name=tuple(name.split(".")),
                        value=new_value,
                        store=self.store,
                        interactive=True,
                    )
                    click.echo()
                    click.pause()
                    return InteractionStatus.SKIP
                except Exception as e:
                    self.tracker.track_command_event(CliEvent.inflight)
                    click.secho(f"Failed to set value: {e}", fg="red")

        elif action.lower() == "n":
            return InteractionStatus.SKIP

        elif action.lower() == "e":
            return InteractionStatus.EXIT
        return None

    def configure_all(self) -> None:
        """Configure all settings."""
        numeric_choices = [idx for idx, _, _ in self.setting_choices]
        if not numeric_choices:
            click.secho(
                "There are no settings to configure. "
                "For help, please see https://melta.no#no-plugin-settings-defined",
                fg="yellow",
            )
            self.tracker.track_command_event(CliEvent.completed)
            return

        while True:
            click.clear()
            self._print_home_screen()
            choices = ["all", *numeric_choices, "e"]

            branch = "all"
            try:
                click.echo()
                branch = click.prompt(
                    "Loop through all settings (all), select a setting by "
                    f"number ({min(int(chs) for chs in numeric_choices)} - "
                    f"{max(int(chs) for chs in numeric_choices)}), or exit (e)?",
                    type=click.Choice(choices, case_sensitive=False),
                    default="all",
                    show_choices=False,
                )
            except click.Abort:
                click.echo()
                branch = "e"

            if branch == "all":
                for index, name, _ in self.setting_choices:
                    click.clear()
                    status = InteractionStatus.START
                    while status not in {
                        InteractionStatus.SKIP,
                        InteractionStatus.EXIT,
                    }:
                        status = self.configure(
                            name=name,
                            index=index,
                            last_index=len(self.setting_choices),
                        )
                    if status == InteractionStatus.EXIT:
                        break
            elif branch.lower() == "e":
                self.tracker.track_command_event(CliEvent.completed)
                click.echo()
                return
            else:
                choice_name = next(
                    nme for idx, nme, _ in self.setting_choices if idx == branch
                )
                click.clear()
                status = self.configure(
                    name=choice_name,
                    index=branch,
                    last_index=len(self.setting_choices),
                    show_set_prompt=False,
                )

    def set_value(self, setting_name, value, store, *, interactive=False) -> None:  # noqa: ANN001
        """Set value helper function."""
        settings = self.settings
        path = list(setting_name)
        try:
            value, metadata = settings.set_with_metadata(
                path,
                value,
                store=store,
                session=self.session,
            )
        except StoreNotSupportedError:
            if interactive:
                self.tracker.track_command_event(CliEvent.inflight)
            else:
                self.tracker.track_command_event(CliEvent.aborted)
            raise

        name = metadata["name"]
        store = metadata["store"]
        setting = metadata["setting"]
        is_redacted = self.safe and setting and setting.is_redacted

        click.secho(
            (
                f"{settings.label.capitalize()} setting '{name}' was set in "
                f"{store.label}: "
            ),
            fg="green",
            nl=False,
        )
        click.secho(
            REDACTED_VALUE if is_redacted else f"{value!r}",
            fg="yellow" if is_redacted else "green",
        )

        current_value, source = settings.get_with_source(name, session=self.session)
        if source != store:
            current_value = REDACTED_VALUE if is_redacted else f"{current_value!r}"

            click.secho(
                f"Current value is still: {current_value} (from {source.label})",
                fg="yellow",
            )

        if interactive:
            self.tracker.track_command_event(CliEvent.inflight)
        else:
            self.tracker.track_command_event(CliEvent.completed)
