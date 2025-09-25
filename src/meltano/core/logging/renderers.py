"""Custom structlog renderers."""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from io import StringIO

import structlog.dev
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from meltano.core.logging.models import PluginException

if t.TYPE_CHECKING:
    from collections.abc import MutableMapping

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
        text = Text()
        text.append("  File ", style="dim")
        text.append(f'"{frame.filename}"', style="cyan")
        text.append(", line ", style="dim")
        text.append(str(frame.lineno), style="yellow")
        text.append(", in ", style="dim")
        text.append(frame.function, style="blue")
        return text

    def format_exception_chain(self, exc: PluginException, *, depth: int = 0) -> Tree:
        """Render the exception chain as a tree.

        Args:
            exc: The exception to render.
            depth: The depth of the exception chain.

        Returns:
            The rendered exception chain.
        """
        # Create the main exception node
        exc_text = Text()
        exc_text.append(f"{exc.module}.{exc.type}", style="bold red")
        exc_text.append(f": {exc.message}", style="red")

        tree = Tree(exc_text)

        # Add traceback if present
        if exc.traceback:
            tb_tree = tree.add(Text("Traceback:", style="bold yellow"))
            for frame in exc.traceback:
                tb_tree.add(self.render_traceback_frame(frame))

        # Add cause chain
        if exc.cause:
            cause_tree = tree.add(Text("Caused by:", style="bold magenta"))
            cause_tree.add(self.format_exception_chain(exc.cause, depth=depth + 1))

        # Add context chain
        if exc.context:
            context_tree = tree.add(Text("During handling of:", style="bold blue"))
            context_tree.add(self.format_exception_chain(exc.context, depth=depth + 1))

        return tree

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
            f"[bold red]Exception Details for {plugin_name}[/bold red]"
            if plugin_name
            else "[bold red]Exception Details[/bold red]"
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
                border_style="red",
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
