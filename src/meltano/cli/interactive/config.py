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
from meltano.core.settings_service import SettingValueStore
from meltano.core.settings_store import StoreNotSupportedError

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
        self.project = self.ctx.obj["project"]
        self.settings = self.ctx.obj["settings"]
        self.session = self.ctx.obj["session"]
        self.plugin = self.ctx.obj["settings"].plugin
        self.environment_service = EnvironmentService(self.project)
        self.max_width = 75
        self.console = Console()

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

    def truncate(self, text: str) -> str:
        """Truncate text."""
        return f"{text[: self.max_width - 3]}..."

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

        # title
        pre = []
        pre.append(
            Text.from_markup(
                f"[bold underline][{PLUGIN_COLOR}]{self.settings.label.capitalize()}[/{PLUGIN_COLOR}][/bold underline] Setting {index} of {last_index}"
            )
        )
        # setting is custom or extra
        if setting_def.is_extra:
            pre.append(
                Text.from_markup(
                    "[yellow1]Custom Extra: plugin-specific options handled by Meltano[/yellow1]"
                )
            )
        elif setting_def.is_custom:
            pre.append(
                Text.from_markup(
                    "[yellow]Custom Setting: possibly unsupported by the plugin[/yellow1]"
                )
            )
        # setting name
        details.add_row(
            Text("Name"), Text.from_markup(f"[{SETTING_COLOR}]{name}[/{SETTING_COLOR}]")
        )
        # current value
        if source is SettingValueStore.DEFAULT:
            label = "default"
        elif source is SettingValueStore.INHERITED:
            label = f"inherited from '{self.settings.plugin.parent.name}'"
        else:
            label = f"from {source.label}"
        expanded_value = value
        unexpanded_value = config_metadata.get("unexpanded_value")
        if unexpanded_value:
            current_value = unexpanded_value or ""
            details.add_row(Text("Current Expanded Value"), Text(f"'{expanded_value}'"))
        else:
            current_value = value or ""
        details.add_row(
            Text(f"Current Value ({label})"),
            Text.from_markup(f"[{VALUE_COLOR}]'{current_value}'[/{VALUE_COLOR}]"),
        )
        # setting kind
        if setting_def.kind:
            details.add_row(Text("Kind"), Text(f"{setting_def.kind}"))
        # default value
        if source is not SettingValueStore.DEFAULT:
            default_value = setting_def.value
            if default_value is not None:
                details.add_row(Text("Default"), Text(f"{default_value!r}"))
        # env vars
        env_keys = [
            var.definition for var in self.settings.setting_env_vars(setting_def)
        ]
        details.add_row(Text("Env(s)"), Text(f"{', '.join(env_keys)}"))
        # setting description (markdown)
        post = []
        if setting_def.description:
            post.append(
                Group(
                    Text(" Description:"),
                    Panel(Markdown(setting_def.description, justify="left")),
                )
            )
        # docs url
        docs_url = self.settings.docs_url
        if docs_url:
            post.append(
                Text.from_markup(
                    f" To learn more about {self.settings.label} and its settings, visit [link={docs_url}]{docs_url}[/link]"
                )
            )
        self.console.print(Panel(Group(*pre, details, *post)))

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
        click.echo()

        action = click.prompt(
            "Set this value (Y/n) or exit (e)?",
            default="y",
            type=click.Choice(["y", "n", "e"], case_sensitive=False),
        )
        if action.lower() == "y":
            new_value = click.prompt("New value", default="", show_default=False)
            click.echo()
            self.set_value(
                setting_name=tuple(name.split(".")),
                value=new_value,
                store=self.store,
            )
            click.echo()
            click.pause()
        elif action.lower() == "n":
            return InteractionStatus.SKIP
        else:
            return InteractionStatus.EXIT

    def configure_all(self):
        """Configure all settings."""
        while True:
            click.clear()
            self._print_home_screen()
            click.echo()
            choices = ["all"] + [idx for idx, _, _ in self.setting_choices] + ["e"]
            branch = click.prompt(
                "Loop through all settings (all), select a setting by number, or exit (e)?",
                type=click.Choice(choices, case_sensitive=False),
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
            elif branch.lower() == "e":
                click.echo()
                break
            else:
                choice_name = next(
                    (nme for idx, nme, _ in self.setting_choices if idx == branch)
                )
                click.clear()
                status = self.configure(
                    name=choice_name,
                    index=branch,
                    last_index=len(self.setting_choices),
                    show_set_prompt=False,
                )

    def set_value(self, setting_name, value, store):
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
            raise CliError(
                f"{settings.label.capitalize()} setting '{path}' could not be set in {store.label}: {err}"
            ) from err

        name = metadata["name"]
        store = metadata["store"]
        click.secho(
            f"{settings.label.capitalize()} setting '{name}' was set in {store.label}: {value!r}",
            fg=VALUE_COLOR,
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
            fg=VALUE_COLOR,
        )

        current_value, source = settings.get_with_source(name, session=self.session)
        if source is not SettingValueStore.DEFAULT:
            click.secho(
                f"Current value is now: {current_value!r} (from {source.label})",
                fg="yellow",
            )
