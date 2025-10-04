"""Custom structlog renderers."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from io import StringIO

import structlog.dev
from rich.console import Console, group
from rich.constrain import Constrain
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import PathHighlighter

from meltano.core.logging.models import PluginException

if t.TYPE_CHECKING:
    from collections.abc import MutableMapping

    from rich.console import RenderResult
    from structlog.typing import WrappedLogger

    from meltano.core.logging.models import TracebackFrame


@dataclass
class StructuredExceptionFormatter:
    """A renderer for Singer exceptions using the rich package."""

    no_color: bool | None = None
    color_system: t.Literal["auto", "standard", "256", "truecolor", "windows"] = (
        "truecolor"
    )
    force_terminal: bool | None = None
    width: int | None = None
    legacy_windows: bool | None = None

    @group()
    def _render_traceback(self, traceback: list[TracebackFrame]) -> RenderResult:
        """Render a single exception.

        Args:
            traceback: The traceback frames to render.

        Returns:
            The rendered traceback.
        """
        path_highlighter = PathHighlighter()

        yield ""

        frames = list(reversed(traceback[-3:]))
        num_skipped = max(len(traceback) - 3, 0)
        for frame in frames:
            yield Text.assemble(
                path_highlighter(Text(frame.filename, style="pygments.string")),
                (":", "pygments.text"),
                (str(frame.lineno), "pygments.number"),
                " in ",
                (frame.function, "pygments.function"),
                style="pygments.text",
            )
            yield ""
            yield Syntax(
                frame.line.rstrip(),
                "python",
                start_line=frame.lineno,
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme=Syntax.get_theme("ansi_dark"),
            )
            yield ""

        if num_skipped > 0:
            yield Text(
                f"... {num_skipped} frames hidden ...",
                justify="center",
                style="traceback.error",
            )

    @group()
    def render_exception(
        self,
        exc: PluginException,
        *,
        plugin_name: str | None = None,
    ) -> RenderResult:
        """Render the exception chain.

        Args:
            exc: The exception to render.
            plugin_name: The name of the plugin.

        Returns:
            The rendered exception chain.
        """
        title = (
            f"[traceback.title]Error details for {plugin_name}"
            if plugin_name
            else "[traceback.title]Error details"
        )
        highlighter = ReprHighlighter()

        if exc.traceback:
            panel = Panel(
                self._render_traceback(exc.traceback),
                title=title,
                border_style="traceback.border",
                expand=True,
                padding=(0, 1),
            )
            yield Constrain(panel, self.width)

        yield Text.assemble(
            (f"{exc.type}: ", "traceback.exc_type"),
            highlighter(exc.message),
        )

        # Add cause chain
        if exc.cause:
            yield Text.from_markup(
                "\n[i]The above exception was the direct cause of the following exception:\n",  # noqa: E501
            )
            yield self.render_exception(exc.cause)

        # Add context chain
        if exc.context:
            yield Text.from_markup(
                "\n[i]During handling of the above exception, another exception occurred:\n",  # noqa: E501
            )
            yield self.render_exception(exc.context)

    def format(
        self,
        sio: t.TextIO,
        exc: PluginException,
        *,
        plugin_name: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Render the exception to the console.

        Args:
            sio: The stream to render the exception to.
            exc: The exception to render.
            plugin_name: The name of the plugin.
            kwargs: Additional keyword arguments to pass to the Console.
        """
        kwargs.setdefault("file", sio)
        kwargs.setdefault("no_color", self.no_color)
        kwargs.setdefault("force_terminal", self.force_terminal)
        kwargs.setdefault("width", self.width)
        kwargs.setdefault("color_system", self.color_system)
        kwargs.setdefault("legacy_windows", self.legacy_windows)
        Console(**kwargs).print(self.render_exception(exc, plugin_name=plugin_name))


class MeltanoConsoleRenderer(structlog.dev.ConsoleRenderer):  # noqa: TID251
    """Custom console renderer that handles our own data structures."""

    default_keys: t.ClassVar[set[str]] = {
        # Base keys
        "timestamp",
        "level",
        "event",
        "logger",
        "logger_name",
        "stack",
        "exception",
        "exc_info",
        # Plugin subprocess
        "name",
        # Plugin structured logging
        "plugin_exception",
        "metric_info",
    }

    def __init__(
        self,
        *args,  # noqa: ANN002
        plugin_exception_renderer: StructuredExceptionFormatter | None = None,
        all_keys: bool | None = None,
        include_keys: set[str] | None = None,
        **kwargs,  # noqa: ANN003
    ) -> None:
        """Initialize the MeltanoConsoleRenderer.

        Args:
            args: Arguments to pass to the parent class.
            plugin_exception_renderer: The renderer to use for plugin exceptions.
            all_keys: Whether to include all keys in the output.
            include_keys: Whether to include specific keys in the output.
            kwargs: Keyword arguments to pass to the parent class.
        """
        super().__init__(*args, **kwargs)
        self._plugin_exception_formatter = (
            plugin_exception_renderer or StructuredExceptionFormatter()
        )
        self._all_keys = all_keys
        self._include_keys = include_keys

    def __call__(
        self,
        logger: WrappedLogger,
        name: str,
        event_dict: MutableMapping[str, t.Any],
    ) -> str:
        """Render the event dictionary to the console.

        Args:
            logger: Wrapped logger object.
            name: The name of the wrapped logger.
            event_dict: Current context together with the current event. If the context
                was `{"a": 42}` and the event is `"foo"`, the initial event_dict will be
                `{"a": 42, "event": "foo"}`.

        Returns:
            The rendered event dictionary.
        """
        if self._include_keys:
            event_dict = {
                k: v
                for k, v in event_dict.items()
                if k in self.default_keys | self._include_keys
            }
        elif not self._all_keys:
            event_dict = {k: v for k, v in event_dict.items() if k in self.default_keys}

        if (
            (exc := event_dict.pop("plugin_exception", None))  # WOLOLO
            and isinstance(exc, PluginException)
        ):
            sio = StringIO()

            # Add formatted exception info to the event
            event_dict["plugin_exc_type"] = exc.type
            event_dict["plugin_exc_message"] = exc.message

            if name == "error":
                # Render the regular log message
                regular_output = super().__call__(logger, name, event_dict)
                # Then render the exception
                self._plugin_exception_formatter.format(
                    sio,
                    exc,
                    plugin_name=event_dict.get("string_id"),
                )
                return sio.getvalue() + "\n" + regular_output

        return super().__call__(logger, name, event_dict)
