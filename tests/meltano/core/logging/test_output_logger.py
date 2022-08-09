from __future__ import annotations

import json
import logging
import platform
import sys
import tempfile

import mock
import pytest
import structlog
from structlog.testing import LogCapture

from meltano.core.logging.output_logger import Out, OutputLogger


def assert_lines(output, *lines):
    for line in lines:
        assert line in output


class TestOutputLogger:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.NamedTemporaryFile(mode="w+", dir=tmp_path)

    @pytest.fixture
    def subject(self, log):
        return OutputLogger(log.name)

    @pytest.fixture(name="log_output")
    def fixture_log_output(self):
        return LogCapture()

    @pytest.fixture(autouse=True)
    def fixture_configure_structlog(self, log_output):
        original_config = structlog.get_config()
        structlog.configure(
            processors=[log_output],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
        )
        try:
            yield
        finally:
            structlog.configure(**original_config)

    @pytest.fixture(name="redirect_handler")
    def redirect_handler(self, subject: OutputLogger) -> logging.Handler:
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),  # use a json renderer so output is easier to verify
        )
        handler = logging.FileHandler(subject.file)
        handler.setFormatter(formatter)
        return handler

    @pytest.mark.asyncio
    async def test_stdio_capture(self, log, subject, log_output):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        stdout_out = subject.out("stdout")
        stderr_out = subject.out("stderr")

        async with stdout_out.redirect_stdout():
            sys.stdout.write("STD")
            sys.stdout.write("OUT\n")
            print("STDOUT 2")  # noqa: WPS421

        assert_lines(
            log_output.entries,
            {
                "name": "stdout",
                "event": "STDOUT",
                "log_level": "info",
            },
            {
                "name": "stdout",
                "event": "STDOUT 2",
                "log_level": "info",
            },
        )

        async with stderr_out.redirect_stderr():
            sys.stderr.write("STD")
            sys.stderr.write("ERR\n")
            print("STDERR 2", file=sys.stderr)  # noqa: WPS421

        assert_lines(
            log_output.entries,
            {
                "name": "stderr",
                "event": "STDERR",
                "log_level": "info",
            },
            {
                "name": "stderr",
                "event": "STDERR 2",
                "log_level": "info",
            },
        )

    @pytest.mark.asyncio
    async def test_out_writers(self, log, subject, log_output):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        writer_out = subject.out("writer")
        line_writer_out = subject.out("lwriter")
        basic_out = subject.out("basic")

        async with writer_out.writer() as writer:
            writer.write("WRI")
            writer.write("TER\n")
            writer.write("WRITER 2\n")

        with line_writer_out.line_writer() as line_writer:
            line_writer.write("LINE\n")
            line_writer.write("LINE 2\n")

        basic_out.writeline("LINE\n")
        basic_out.writeline("LINE 2\n")

        assert_lines(
            log_output.entries,
            {
                "name": "writer",
                "event": "WRITER",
                "log_level": "info",
            },
            {
                "name": "writer",
                "event": "WRITER 2",
                "log_level": "info",
            },
            {
                "name": "lwriter",
                "event": "LINE",
                "log_level": "info",
            },
            {
                "name": "lwriter",
                "event": "LINE 2",
                "log_level": "info",
            },
            {"name": "basic", "event": "LINE", "log_level": "info"},
            {
                "name": "basic",
                "event": "LINE 2",
                "log_level": "info",
            },
        )

    @pytest.mark.asyncio
    async def test_set_custom_logger(self, log, subject, log_output):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        logger = structlog.getLogger()
        out = subject.out("basic", logger.bind(is_test=True))

        out.writeline("LINE\n")
        assert_lines(
            log_output.entries,
            {
                "name": "basic",
                "event": "LINE",
                "log_level": "info",
                "is_test": True,
            },
        )

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    @pytest.mark.asyncio
    async def test_logging_redirect(self, log, subject, log_output, redirect_handler):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        logging_out = subject.out("logging")

        with mock.patch.object(Out, "redirect_log_handler", redirect_handler):
            with logging_out.redirect_logging():
                logging.info("info")
                logging.warning("warning")
                logging.error("error")

        with open(subject.file) as logf:
            log_file_contents = [json.loads(line) for line in logf.readlines()]

        assert_lines(
            log_file_contents,
            {"event": "info"},
            {"event": "warning"},
            {"event": "error"},
        )

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Test fails if even attempted to be run, xfail can't save us here.",
    )
    def test_logging_exception(self, log, subject, redirect_handler):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        logging_out = subject.out("logging")

        # it raises logs unhandled exceptions
        exception = Exception("exception")

        with pytest.raises(Exception) as exc:
            with mock.patch.object(Out, "redirect_log_handler", redirect_handler):
                with logging_out.redirect_logging():
                    raise exception

        # make sure it let the exception through
        # All code below here in this test cannot be reached
        assert exc.value is exception

        log_content = json.loads(log.read())

        # make sure the exception is logged
        assert log_content.get("event") == "exception"
        assert log_content.get("exc_info")
