from __future__ import annotations

import typing as t
from contextlib import redirect_stdout
from io import StringIO
from textwrap import dedent

import pytest
from rich.console import Console

from meltano.core.logging.models import SingerSDKException, TracebackFrame
from meltano.core.logging.renderers import (
    RichStructuredExceptionRenderer,
    StructlogExceptionProcessor,
)

if t.TYPE_CHECKING:
    from pytest_subtests import SubTests


class TestRichStructuredExceptionRenderer:
    @pytest.fixture
    def subject(self) -> RichStructuredExceptionRenderer:
        console = Console(no_color=True)
        return RichStructuredExceptionRenderer(console=console)

    @pytest.fixture
    def exception(self) -> SingerSDKException:
        return SingerSDKException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
            cause=SingerSDKException(
                type="ValueError",
                module="builtins",
                message="Invalid value provided",
                traceback=[
                    TracebackFrame(
                        filename="my_module.py",
                        function="my_function",
                        lineno=8,
                    ),
                ],
                context=SingerSDKException(
                    type="ValueError",
                    module="builtins",
                    message="An invalid value was provided",
                ),
            ),
            traceback=[
                TracebackFrame(
                    filename="my_module.py",
                    function="my_function",
                    lineno=10,
                ),
            ],
        )

    @pytest.fixture
    def expected_output(self) -> str:
        return dedent("""\
            ╭───────────────────────────── Exception Details ──────────────────────────────╮
            │ my_package.my_module.CustomException: Custom exception message               │
            │ ├── Traceback:                                                               │
            │ │   └──   File "my_module.py", line 10, in my_function                       │
            │ └── Caused by:                                                               │
            │     └── builtins.ValueError: Invalid value provided                          │
            │         ├── Traceback:                                                       │
            │         │   └──   File "my_module.py", line 8, in my_function                │
            │         └── During handling of:                                              │
            │             └── builtins.ValueError: An invalid value was provided           │
            ╰──────────────────────────────────────────────────────────────────────────────╯
        """)  # noqa: E501

    def test_render_to_console(
        self,
        subject: RichStructuredExceptionRenderer,
        exception: SingerSDKException,
        expected_output: str,
    ) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            subject.render_to_console(exception)

        buffer.seek(0)
        assert buffer.getvalue() == expected_output

    def test_structlog_processor(
        self,
        subtests: SubTests,
        subject: RichStructuredExceptionRenderer,
        exception: SingerSDKException,
        expected_output: str,
    ) -> None:
        processor = StructlogExceptionProcessor(renderer=subject)
        event_dict = {"exception": exception}

        with subtests.test(msg="error"):
            buffer = StringIO()
            with redirect_stdout(buffer):
                updated_event_dict = processor(None, "error", event_dict)

            assert updated_event_dict == {
                "exc_type": "my_package.my_module.CustomException",
                "exc_message": "Custom exception message",
            }
            buffer.seek(0)
            assert buffer.getvalue() == expected_output

        with subtests.test(msg="warning"):
            buffer = StringIO()
            with redirect_stdout(buffer):
                updated_event_dict = processor(None, "warning", event_dict)

            assert updated_event_dict == {
                "exc_type": "my_package.my_module.CustomException",
                "exc_message": "Custom exception message",
            }
            buffer.seek(0)
            assert buffer.getvalue() == ""
