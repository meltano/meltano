from __future__ import annotations

import functools
import json
from io import StringIO
from textwrap import dedent

import pytest
import structlog
import structlog.processors

from meltano.core.logging.models import PluginException, TracebackFrame
from meltano.core.logging.renderers import (
    MeltanoConsoleRenderer,
    PluginErrorFormatter,
    PluginInstallFormatter,
)
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallState,
    PluginInstallStatus,
)


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
def install_state() -> PluginInstallState:
    return PluginInstallState(
        plugin=ProjectPlugin(name="tap-mock", plugin_type=PluginType.EXTRACTORS),
        reason=PluginInstallReason.INSTALL,
        status=PluginInstallStatus.ERROR,
        message="Custom exception message",
        details=(
            "This is multi-line error message.\n\nDetails of the error are "
            "contained here."
        ),
    )


@pytest.fixture
def error_formatter() -> PluginErrorFormatter:
    return PluginErrorFormatter(
        force_terminal=False,
        width=80,
        no_color=True,
        color_system="auto",
        legacy_windows=False,
    )


@pytest.fixture
def install_formatter() -> PluginInstallFormatter:
    return PluginInstallFormatter(
        force_terminal=False,
        width=80,
        no_color=True,
        color_system="auto",
        legacy_windows=False,
    )


@pytest.fixture
def expected_exception_output() -> str:
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


@pytest.fixture
def expected_install_output() -> str:
    return dedent("""\
        ╭───────────────────────────── Installation error ─────────────────────────────╮
        │ This is multi-line error message.                                            │
        │                                                                              │
        │ Details of the error are contained here.                                     │
        ╰────────────────────────── Custom exception message ──────────────────────────╯
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
    def test_simple_exception(self, error_formatter: PluginErrorFormatter) -> None:
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
        )
        buffer = StringIO()
        error_formatter.format(buffer, exception)
        assert buffer.getvalue() == "CustomException: Custom exception message\n"

    def test_no_tracebacks(self, error_formatter: PluginErrorFormatter) -> None:
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
        error_formatter.format(buffer, exception)
        assert buffer.getvalue() == (
            "CustomException: Custom exception message\n\n"
            "The above exception was the direct cause of the following exception:\n\n"
            "ValueError: Invalid value provided\n"
        )

    def test_hidden_tracebacks(self, error_formatter: PluginErrorFormatter) -> None:
        expected_output = dedent("""\
        ╭─────────────────────────────── Error details ────────────────────────────────╮
        │                                                                              │
        │ my_module.py:5 in my_function                                                │
        │                                                                              │
        │   5 raise RuntimeError()                                                     │
        │                                                                              │
        │ my_module.py:4 in my_function                                                │
        │                                                                              │
        │   4 raise RuntimeError()                                                     │
        │                                                                              │
        │ my_module.py:3 in my_function                                                │
        │                                                                              │
        │   3 raise RuntimeError()                                                     │
        │                                                                              │
        │                           ... 3 frames hidden ...                            │
        ╰──────────────────────────────────────────────────────────────────────────────╯
        CustomException: Custom exception message
        """)
        exception = PluginException(
            type="CustomException",
            module="my_package.my_module",
            message="Custom exception message",
            traceback=[
                TracebackFrame(
                    filename="my_module.py",
                    function="my_function",
                    lineno=i,
                    line="raise RuntimeError()",
                )
                for i in range(6)
            ],
        )
        buffer = StringIO()
        error_formatter.format(buffer, exception)
        assert buffer.getvalue() == expected_output

    def test_render(
        self,
        error_formatter: PluginErrorFormatter,
        exception: PluginException,
        expected_exception_output: str,
    ) -> None:
        buffer = StringIO()
        error_formatter.format(buffer, exception)
        assert buffer.getvalue() == expected_exception_output


class TestPluginInstallFormatter:
    def test_render(
        self,
        install_formatter: PluginInstallFormatter,
        expected_install_output: str,
        install_state: PluginInstallState,
    ) -> None:
        buffer = StringIO()
        install_formatter.format(buffer, install_state)
        assert buffer.getvalue() == expected_install_output

    def test_render_without_details(
        self,
        install_formatter: PluginInstallFormatter,
        install_state: PluginInstallState,
    ) -> None:
        buffer = StringIO()
        state = PluginInstallState(
            plugin=install_state.plugin,
            reason=install_state.reason,
            status=install_state.status,
            details=None,
        )
        install_formatter.format(buffer, state)
        assert buffer.getvalue() == ""


class TestMeltanoConsoleRenderer:
    @pytest.fixture
    def subject(
        self,
        error_formatter: PluginErrorFormatter,
        install_formatter: PluginInstallFormatter,
    ) -> MeltanoConsoleRenderer:
        return MeltanoConsoleRenderer(
            plugin_error_renderer=error_formatter,
            plugin_install_renderer=install_formatter,
            colors=False,
            all_keys=True,
        )

    def test_included_keys(
        self,
        error_formatter: PluginErrorFormatter,
        exception: PluginException,
        subtests: pytest.Subtests,
    ) -> None:
        make_renderer = functools.partial(
            MeltanoConsoleRenderer,
            plugin_error_renderer=error_formatter,
            colors=False,
        )

        def get_event_dict() -> dict:
            return {
                # Base keys
                "timestamp": "2021-01-01T00:00:00Z",
                "level": "info",
                "event": "Something happened",
                # Plugin subprocess
                "name": "tap-mock",
                # Plugin structured logging
                "plugin_exception": exception,
                "metric_info": {
                    "type": "counter",
                    "metric": "record_count",
                    "value": 1500,
                    "tags": {
                        "stream": "users",
                        "tap": "tap-example",
                    },
                },
                # Extra keys
                "job_name": "dev:tap-mock-to-target-mock",
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "foo": "bar",
            }

        event_dict = get_event_dict()
        with subtests.test(msg="default"):
            renderer = make_renderer()
            result = renderer(None, "info", event_dict)
            # Plugin name is now rendered as a column, not key=value
            assert "tap-mock" in result
            assert "name=tap-mock" not in result  # Column, not key=value
            # Auto-added keys
            assert "plugin_exc_message=" in result
            assert "plugin_exc_type=" in result
            # Extra keys (not included)
            assert "job_name=dev:tap-mock-to-target-mock" not in result
            assert "run_id=123e4567-e89b-12d3-a456-426614174000" not in result
            assert "foo=bar" not in result

        event_dict = get_event_dict()
        with subtests.test(msg="all keys"):
            renderer = make_renderer(all_keys=True)
            result = renderer(None, "info", event_dict)
            # Plugin name is now rendered as a column, not key=value
            assert "tap-mock" in result
            assert "name=tap-mock" not in result  # Column, not key=value
            # Auto-added keys
            assert "plugin_exc_message=" in result
            assert "plugin_exc_type=" in result
            # Extra keys (included)
            assert "job_name=dev:tap-mock-to-target-mock" in result
            assert "run_id=123e4567-e89b-12d3-a456-426614174000" in result
            assert "foo=bar" in result

        event_dict = get_event_dict()
        include_keys = {"foo"}
        with subtests.test(msg="include keys"):
            renderer = make_renderer(include_keys=include_keys)
            result = renderer(None, "info", event_dict)
            # Plugin name is now rendered as a column, not key=value
            assert "tap-mock" in result
            assert "name=tap-mock" not in result  # Column, not key=value
            # Auto-added keys
            assert "plugin_exc_message=" in result
            assert "plugin_exc_type=" in result
            # Extra keys (not included)
            assert "job_name=dev:tap-mock-to-target-mock" not in result
            assert "run_id=123e4567-e89b-12d3-a456-426614174000" not in result
            # Extra keys (included)
            assert "foo=bar" in result

    def test_console_output_from_plugin_error(
        self,
        subtests: pytest.Subtests,
        error_formatter: PluginErrorFormatter,
        exception: PluginException,
        expected_exception_output: str,
    ) -> None:
        def key_val(*cols, **kwargs) -> str:
            elems = (
                *cols,
                *(f"{k}={v}" for k, v in kwargs.items()),
            )
            return " ".join(elems)

        renderer = MeltanoConsoleRenderer(
            plugin_error_renderer=error_formatter,
            colors=False,
            include_keys={"key"},
        )
        meltano_col = f"{'meltano':<12}"

        with subtests.test(msg="error"):
            out = renderer(None, "error", {"plugin_exception": exception})
            assert out == expected_exception_output + "\n" + key_val(
                meltano_col,
                plugin_exc_message="'Custom exception message'",
                plugin_exc_type="CustomException",
            )

        with subtests.test(msg="warning"):
            out = renderer(None, "warning", {"plugin_exception": exception})
            assert out == key_val(
                meltano_col,
                plugin_exc_message="'Custom exception message'",
                plugin_exc_type="CustomException",
            )

        with subtests.test(msg="no exception"):
            out = renderer(None, "warning", {"key": "value"})
            assert out == key_val(meltano_col, key="value")

    def test_console_output_from_plugin_install(
        self,
        install_formatter: PluginInstallFormatter,
        expected_install_output: str,
        install_state: PluginInstallState,
    ) -> None:
        renderer = MeltanoConsoleRenderer(
            plugin_install_renderer=install_formatter,
            colors=False,
        )

        out = renderer(None, "install", {"install_state": install_state})
        # Install output is followed by the log line with columns
        assert expected_install_output in out
        # Default name column should show "meltano"
        assert "meltano" in out

    def test_console_output_from_metric_info(
        self,
        subject: MeltanoConsoleRenderer,
    ) -> None:
        event_dict = {
            "metric_info": {
                "type": "counter",
                "metric": "record_count",
                "value": 1500,
                "tags": {
                    "stream": "users",
                    "tap": "tap-example",
                },
            }
        }
        out = subject(None, "info", event_dict)
        assert "metric_name=record_count" in out
        assert "metric_value=1500" in out

    def test_default_name_column(
        self,
        error_formatter: PluginErrorFormatter,
    ) -> None:
        """Test that 'meltano' appears as default when name is missing."""
        renderer = MeltanoConsoleRenderer(
            plugin_error_renderer=error_formatter,
            colors=False,
        )

        # No "name" key - should default to "meltano"
        event_dict_missing_name = {
            "timestamp": "2021-01-01T00:00:00Z",
            "level": "info",
            "event": "Something happened",
        }

        result = renderer(None, "info", event_dict_missing_name)
        # "meltano" should appear as a column (default value)
        assert "meltano" in result
        # It should NOT appear as key=value
        assert "name=meltano" not in result
        # The event should be rendered
        assert "Something happened" in result

        # `None` "name" key - should default to "meltano"
        event_dict_none_name = {
            "timestamp": "2021-01-01T00:00:00Z",
            "level": "info",
            "event": "Something happened",
            "name": None,
        }
        result = renderer(None, "info", event_dict_none_name)
        assert "meltano" in result

        # Empty "name" key - should default to "meltano"
        event_dict_empty_name = {
            "timestamp": "2021-01-01T00:00:00Z",
            "level": "info",
            "event": "Something happened",
            "name": "",
        }
        result = renderer(None, "info", event_dict_empty_name)
        assert "meltano" in result

    def test_plugin_name_column(
        self,
        error_formatter: PluginErrorFormatter,
    ) -> None:
        """Test that plugin name appears in its own column."""
        renderer = MeltanoConsoleRenderer(
            plugin_error_renderer=error_formatter,
            colors=False,
        )

        event_dict = {
            "timestamp": "2021-01-01T00:00:00Z",
            "level": "info",
            "event": "Something happened",
            "name": "tap-mock",
        }

        result = renderer(None, "info", event_dict)
        # Plugin name should appear as a column
        assert "tap-mock" in result
        # It should NOT appear as key=value
        assert "name=tap-mock" not in result
        # The event should be rendered
        assert "Something happened" in result
        # Verify column order: name should come before event
        name_pos = result.find("tap-mock")
        event_pos = result.find("Something happened")
        assert name_pos < event_pos, "Plugin name should appear before event"
