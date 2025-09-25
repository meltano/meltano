"""Custom structlog renderers."""

from __future__ import annotations

import typing as t

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from meltano.core.logging.models import SingerSDKException

if t.TYPE_CHECKING:
    from collections.abc import MutableMapping

    from meltano.core.logging.models import TracebackFrame


class RichStructuredExceptionRenderer:
    """A renderer for Singer exceptions using the rich package."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the RichExceptionRenderer."""
        self.console = console or Console()

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

    def render_exception_chain(
        self, exc: SingerSDKException, *, depth: int = 0
    ) -> Tree:
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
            cause_tree.add(self.render_exception_chain(exc.cause, depth=depth + 1))

        # Add context chain
        if exc.context:
            context_tree = tree.add(Text("During handling of:", style="bold blue"))
            context_tree.add(self.render_exception_chain(exc.context, depth=depth + 1))

        return tree

    def render_to_console(self, exc: SingerSDKException) -> None:
        """Render the exception to the console.

        Args:
            exc: The exception to render.
        """
        panel = Panel(
            self.render_exception_chain(exc),
            title="[bold red]Exception Details[/bold red]",
            border_style="red",
        )
        self.console.print(panel)


class StructlogExceptionProcessor:
    """Custom structlog processor for SingerException objects."""

    def __init__(self, renderer: RichStructuredExceptionRenderer | None = None) -> None:
        """Initialize the StructlogExceptionProcessor.

        Args:
            renderer: The renderer to use.
        """
        self.renderer = renderer or RichStructuredExceptionRenderer()

    def __call__(
        self,
        logger: t.Any,  # noqa: ANN401, ARG002
        method_name: str,
        event_dict: MutableMapping[str, t.Any],
    ) -> MutableMapping[str, t.Any]:
        """Process log events containing SingerException.

        Docs: https://www.structlog.org/en/stable/processors.html.

        Args:
            logger: Wrapped logger object.
            method_name: The name of the wrapped method. If you called
                `log.warning("foo")`, it will be `"warning"`.
            event_dict: Current context together with the current event. If the context
                was `{"a": 42}` and the event is `"foo"`, the initial event_dict will be
                `{"a": 42, "event": "foo"}`.

        Returns:
            The event dictionary.
        """
        if (
            "exception" in event_dict  # TODO: Rename to "sdk_exception"?
            and isinstance(event_dict["exception"], SingerSDKException)
        ):
            exc = event_dict["exception"]

            # Add formatted exception info to the event
            event_dict["exc_type"] = f"{exc.module}.{exc.type}"
            event_dict["exc_message"] = exc.message

            # If this is an ERROR level log, we might want to render it
            if method_name == "error":
                self.renderer.render_to_console(exc)
                # Remove the raw exception object to avoid double rendering
                event_dict.pop("exception", None)

        return event_dict
