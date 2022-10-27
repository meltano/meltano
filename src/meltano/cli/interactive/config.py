"""Interactive configuration handler."""

from __future__ import annotations

import contextlib
import json

import click
from jinja2 import BaseLoader, Environment
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from meltano.cli.interactive.utils import InteractionStatus
from meltano.cli.utils import CliError
from meltano.core.environment_service import EnvironmentService
from meltano.core.project import Project
from meltano.core.settings_service import (
    REDACTED_VALUE,
    SettingKind,
    SettingsService,
    SettingValueStore,
)
from meltano.core.settings_store import StoreNotSupportedError
from meltano.core.tracking import CliEvent

PLUGIN_COLOR = "magenta"
ENVIRONMENT_COLOR = "orange1"
SETTING_COLOR = "blue1"
VALUE_COLOR = "green"

HOME_SCREEN_TEMPLATE = """[bold underline]Configuring [{{ plugin_color }}]{{ plugin_name.capitalize() | safe }}[/{{ plugin_color }}] {% if environment_name %}in Environment[{{ environment_color }}]{{ environment_name }}[/{{ environment_color }}] {% endif %}Interactively[/bold underline]

Following the prompts below, you will be guided through configuration of this plugin.

Meltano is responsible for managing the configuration of all of a project’s plugins.
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
"""


class InteractiveConfig:  # noqa: WPS230, WPS214
    """Manage Config interactively."""

    def __init__(self, ctx, store, extras=False, max_width=None):
        """Initialise InteractiveConfig instance."""
        self.ctx = ctx
        self.store = store
        self.extras = extras
        self.project: Project = self.ctx.obj["project"]
        self.settings: SettingsService = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]
        self.tracker = self.ctx.obj["tracker"]
        self.environment_service = EnvironmentService(self.project)
        self.max_width = max_width or 75  # noqa: WPS432
        self.console = Console()

    @property
    def configurable_settings(self):
        """Return settings available for interactive configuration."""
        return self.settings.config_with_metadata(
            session=self.session, extras=self.extras, redacted=True
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

    def truncate(self, text: str) -> str:
        """Truncate text."""
        if len(text) >= self.max_width:
            return f"{text[: self.max_width - 3]}..."
        return text

    def _print_home_screen(self):
        """Print screen for this interactive."""
        markdown_template = Environment(loader=BaseLoader, autoescape=True).from_string(
            HOME_SCREEN_TEMPLATE
        )
        markdown_text = markdown_template.render(
            {
                "plugin_color": PLUGIN_COLOR,
                "environment_color": ENVIRONMENT_COLOR,
                "setting_color": SETTING_COLOR,
                "plugin_name": self.settings.label,
                "plugin_url": self.settings.docs_url,
                "environment_name": self.project.active_environment.name
                if self.project.active_environment
                else None,
                "settings": [
                    {
                        "name": name,
                        "description": self.truncate(description.replace("\n", " ")),
                    }
                    for _, name, description in self.setting_choices
                ],
            }
        )
        self.console.print(Panel(Text.from_markup(markdown_text)))

    def _print_setting(self, name, config_metadata, index, last_index):
        """Print setting."""
        value = config_metadata["value"]
        source = config_metadata["source"]
        setting_def = config_metadata["setting"]
        details = Table(show_header=False)
        details.add_column("name", justify="right")
        details.add_column("value")

        pre = [
            Text.from_markup(
                f"[bold underline][{PLUGIN_COLOR}]{self.settings.label.capitalize()}[/{PLUGIN_COLOR}][/bold underline] Setting {index} of {last_index}"
            )
        ]

        if setting_def.is_extra:
            pre.append(
                Text.from_markup(
                    "[yellow1]Custom Extra: plugin-specific options handled by Meltano[/yellow1]"
                )
            )

        elif setting_def.is_custom:
            pre.append(
                Text.from_markup(
                    "[yellow1]Custom Setting: possibly unsupported by the plugin[/yellow1]"
                )
            )

        details.add_row(
            Text("Name"), Text.from_markup(f"[{SETTING_COLOR}]{name}[/{SETTING_COLOR}]")
        )

        if source is SettingValueStore.DEFAULT:
            label = "default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{self.settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"
        expanded_value = value if value is not None else "(empty string)"
        unexpanded_value = config_metadata.get("unexpanded_value")
        if unexpanded_value:
            current_value = (
                unexpanded_value if unexpanded_value is not None else "(empty string)"
            )

            details.add_row(Text("Current Expanded Value"), Text(f"{expanded_value}"))
        else:
            current_value = value if value is not None else "(empty string)"
        details.add_row(
            Text(f"Current Value ({label})"),
            Text.from_markup(f"[{VALUE_COLOR}]{current_value}[/{VALUE_COLOR}]"),
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
                )
            )

        docs_url = self.settings.docs_url
        if docs_url:
            post.append(
                Text.from_markup(
                    f" To learn more about {self.settings.label} and its settings, visit [link={docs_url}]{docs_url}[/link]"
                )
            )

        self.console.print(Panel(Group(*pre, details, *post)))

    @staticmethod
    def _value_prompt(config_metadata):
        if config_metadata["setting"].kind != SettingKind.OPTIONS:
            return (
                click.prompt(
                    "New value",
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

    def configure(self, name, index=None, last_index=None, show_set_prompt=True):
        """Configure a single setting interactively."""
        config_metadata = next(
            (
                config_metadata
                for nme, config_metadata in self.configurable_settings.items()
                if nme == name
            )
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

    def configure_all(self):
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

    def set_value(self, setting_name, value, store, interactive=False):
        """Set value helper function."""
        with contextlib.suppress(json.JSONDecodeError):
            value = json.loads(value)

        settings = self.settings
        path = list(setting_name)
        try:
            value, metadata = settings.set_with_metadata(
                path, value, store=store, session=self.session
            )
        except StoreNotSupportedError as err:
            if interactive:
                self.tracker.track_command_event(CliEvent.inflight)
            else:
                self.tracker.track_command_event(CliEvent.aborted)
            raise CliError(
                f"{settings.label.capitalize()} setting '{path}' could not be set in {store.label}: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        is_redacted = metadata["setting"] and metadata["setting"].is_redacted
        if is_redacted:
            value = REDACTED_VALUE
        click.secho(
            f"{settings.label.capitalize()} setting '{name}' was set in {store.label}: {value!r}",
            fg=VALUE_COLOR,
        )

        current_value, source = settings.get_with_source(name, session=self.session)
        if source != store:
            if is_redacted:
                current_value = REDACTED_VALUE
            click.secho(
                f"Current value is still: {current_value!r} (from {source.label})",
                fg="yellow",
            )

        if interactive:
            self.tracker.track_command_event(CliEvent.inflight)
        else:
            self.tracker.track_command_event(CliEvent.completed)
