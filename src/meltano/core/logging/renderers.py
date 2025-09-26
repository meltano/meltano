"""Custom structlog renderers."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from io import StringIO

import structlog.dev
from rich.console import Console, group
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

    def render_traceback_frame(self, frame: TracebackFrame) -> Text:
        """Render a single traceback frame.

        Args:
            frame: The traceback frame to render.

        Returns:
            The rendered traceback frame.
        """
        path_highlighter = PathHighlighter()

        return Text.assemble(
            path_highlighter(Text(frame.filename, style="pygments.string")),
            (":", "pygments.text"),
            (str(frame.lineno), "pygments.number"),
            " in ",
            (frame.function, "pygments.function"),
            style="pygments.text",
        )

    @group()
    def format_exception_chain(
        self,
        exc: PluginException,
        *,
        depth: int = 0,
    ) -> RenderResult:
        """Render the exception chain as a tree.

        Args:
            exc: The exception to render.
            depth: The depth of the exception chain.

        Returns:
            The rendered exception chain.
        """
        # Create the main exception node
        yield Text.assemble(
            (f"{exc.module}.{exc.type}", "bold red"),
            (f": {exc.message}", "red"),
        )

        # Add traceback if present
        if exc.traceback:
            yield ""

            frames = list(reversed(exc.traceback[-3:]))
            num_skipped = max(len(exc.traceback) - 3, 0)
            for frame in frames:
                yield self.render_traceback_frame(frame)
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
                    f"\n... {num_skipped} frames hidden ...",
                    justify="center",
                    style="traceback.error",
                )

        # Add cause chain
        # TODO: Make these prettier
        if exc.cause:
            yield Text.assemble(("Caused by:", "bold magenta"))
            yield self.format_exception_chain(exc.cause, depth=depth + 1)

        # Add context chain
        # TODO: Make these prettier
        if exc.context:
            yield Text.assemble(("During handling of:", "bold blue"))
            yield self.format_exception_chain(exc.context, depth=depth + 1)

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
        title = (
            f"[traceback.title]Error Details for {plugin_name}"
            if plugin_name
            else "[traceback.title]Error Details"
        )
        kwargs.setdefault("file", sio)
        kwargs.setdefault("no_color", self.no_color)
        kwargs.setdefault("force_terminal", self.force_terminal)
        kwargs.setdefault("width", self.width)
        kwargs.setdefault("color_system", self.color_system)
        Console(**kwargs).print(
            Panel(
                self.format_exception_chain(exc),
                title=title,
                border_style="traceback.border",
                expand=False,
                padding=(0, 1),
            ),
        )


class MeltanoConsoleRenderer(structlog.dev.ConsoleRenderer):
    """Custom console renderer that handles our own data structures."""

    def __init__(
        self,
        *args,  # noqa: ANN002
        plugin_exception_renderer: StructuredExceptionFormatter | None = None,
        **kwargs,  # noqa: ANN003
    ) -> None:
        """Initialize the MeltanoConsoleRenderer.

        Args:
            args: Arguments to pass to the parent class.
            plugin_exception_renderer: The renderer to use for plugin exceptions.
            kwargs: Keyword arguments to pass to the parent class.
        """
        super().__init__(*args, **kwargs)
        self._plugin_exception_formatter = (
            plugin_exception_renderer or StructuredExceptionFormatter()
        )

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
