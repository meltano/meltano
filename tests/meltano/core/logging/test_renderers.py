from __future__ import annotations

import json
import typing as t
from io import StringIO
from textwrap import dedent

import pytest
import structlog
import structlog.processors

from meltano.core.logging.models import PluginException, TracebackFrame
from meltano.core.logging.renderers import (
    MeltanoConsoleRenderer,
    StructuredExceptionFormatter,
)

if t.TYPE_CHECKING:
    from pytest_subtests import SubTests


@pytest.fixture(autouse=True)
def no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.setenv("NO_COLOR", "1")


@pytest.fixture
def exception() -> PluginException:
    return PluginException(
        type="CustomException",
        module="my_package.my_module",
        message="Custom exception message",
        cause=PluginException(
            type="ValueError",
            module="builtins",
            message="Invalid value provided",
            traceback=[
                TracebackFrame(
                    filename="my_module.py",
                    function="my_function",
                    lineno=8,
                    line="raise ValueError('Invalid value provided')",
                ),
            ],
            context=PluginException(
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
                line="raise CustomException('Custom exception message') from err",
            ),
        ],
    )


@pytest.fixture
def formatter() -> StructuredExceptionFormatter:
    return StructuredExceptionFormatter(
        force_terminal=False,
        width=80,
        no_color=True,
        color_system="auto",
        legacy_windows=False,
    )


@pytest.fixture
def expected_output() -> str:
    return dedent("""\
        ╭─────────────────────────────── Error details ────────────────────────────────╮
        │                                                                              │
        │ my_module.py:10 in my_function                                               │
        │                                                                              │
        │   10 raise CustomException('Custom exception message') from err              │
        │                                                                              │
        ╰──────────────────────────────────────────────────────────────────────────────╯
        CustomException: Custom exception message

        The above exception was the direct cause of the following exception:

        ╭─────────────────────────────── Error details ────────────────────────────────╮
        │                                                                              │
        │ my_module.py:8 in my_function                                                │
        │                                                                              │
        │   8 raise ValueError('Invalid value provided')                               │
        │                                                                              │
        ╰──────────────────────────────────────────────────────────────────────────────╯
        ValueError: Invalid value provided

        During handling of the above exception, another exception occurred:

        ValueError: An invalid value was provided
    """)


class TestPluginException:
    def test_to_dict_and_back(self) -> None:
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
        )
        assert PluginException.from_dict(exception.to_dict()) == exception

        exception_data = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
            traceback=[
                TracebackFrame(
                    filename="my_module.py",
                    function="my_function",
                    lineno=8,
                    line="raise ValueError('Invalid value provided')",
                ),
            ],
            cause=PluginException(
                type="ValueError",
                module="builtins",
                message="Invalid value provided",
            ),
            context=PluginException(
                type="ValueError",
                module="builtins",
                message="An invalid value was provided",
            ),
        )
        assert PluginException.from_dict(exception_data.to_dict()) == exception_data

    def test_to_structlog(self) -> None:
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
        )
        processor = structlog.processors.JSONRenderer()
        logger = structlog.get_logger()
        event_dict = {"plugin_exception": exception}
        assert json.loads(processor(logger, "info", event_dict)) == {
            "plugin_exception": exception.to_dict(),
        }


class TestStructuredExceptionFormatter:
    def test_simple_exception(self, formatter: StructuredExceptionFormatter) -> None:
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
        )
        buffer = StringIO()
        formatter.format(buffer, exception)
        assert buffer.getvalue() == "CustomException: Custom exception message\n"

    def test_no_tracebacks(self, formatter: StructuredExceptionFormatter) -> None:
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
            cause=PluginException(
                type="ValueError",
                module="builtins",
                message="Invalid value provided",
            ),
        )
        buffer = StringIO()
        formatter.format(buffer, exception)
        assert buffer.getvalue() == (
            "CustomException: Custom exception message\n\n"
            "The above exception was the direct cause of the following exception:\n\n"
            "ValueError: Invalid value provided\n"
        )

    def test_render(
        self,
        formatter: StructuredExceptionFormatter,
        exception: PluginException,
        expected_output: str,
    ) -> None:
        buffer = StringIO()
        formatter.format(buffer, exception)
        assert buffer.getvalue() == expected_output


class TestMeltanoConsoleRenderer:
    @pytest.fixture
    def subject(
        self,
        formatter: StructuredExceptionFormatter,
    ) -> MeltanoConsoleRenderer:
        return MeltanoConsoleRenderer(
            plugin_exception_renderer=formatter,
            colors=False,
        )

    def test_console_output(
        self,
        subtests: SubTests,
        subject: MeltanoConsoleRenderer,
        exception: PluginException,
        expected_output: str,
    ) -> None:
        def key_val(**kwargs) -> str:
            return " ".join(f"{k}={v}" for k, v in kwargs.items())

        with subtests.test(msg="error"):
            out = subject(None, "error", {"plugin_exception": exception})
            assert out == expected_output + "\n" + key_val(
                plugin_exc_message="'Custom exception message'",
                plugin_exc_type="CustomException",
            )

        with subtests.test(msg="warning"):
            out = subject(None, "warning", {"plugin_exception": exception})
            assert out == key_val(
                plugin_exc_message="'Custom exception message'",
                plugin_exc_type="CustomException",
            )

        with subtests.test(msg="no exception"):
            out = subject(None, "warning", {"key": "value"})
            assert out == key_val(key="value")
