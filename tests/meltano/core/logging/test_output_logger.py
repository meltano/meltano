import io
import logging
import sys
import tempfile
from pathlib import Path

import pytest
from meltano.core.logging.output_logger import OutputLogger


def assert_lines(output, *lines):
    for line in lines:
        assert line in output


class TestOutputLogger:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.TemporaryFile(mode="w+", dir=tmp_path)
        # return io.StringIO()

    @pytest.fixture
    def subject(self, log):
        return OutputLogger(log)

    @pytest.mark.asyncio
    async def test_out(self, log, subject):
        stdout_out = subject.out("stdout")
        stderr_out = subject.out("stderr")
        logging_out = subject.out("logging")
        writer_out = subject.out("writer")
        line_writer_out = subject.out("lwriter")
        basic_out = subject.out("basic")
        subtask_out = subject.out("basic", subtask_name="subtask")

        async with stdout_out.redirect_stdout():
            sys.stdout.write("STD")
            sys.stdout.write("OUT\n")
            print("STDOUT 2")

        async with stderr_out.redirect_stderr():
            sys.stderr.write("STD")
            sys.stderr.write("ERR\n")
            print("STDERR 2", file=sys.stderr)

        with logging_out.redirect_logging():
            logging.info("info")
            logging.warning("warning")
            logging.error("error")

        async with writer_out.writer() as writer:
            writer.write("WRI")
            writer.write("TER\n")
            writer.write("WRITER 2\n")

        with line_writer_out.line_writer() as line_writer:
            line_writer.write("LINE\n")
            line_writer.write("LINE 2\n")

        basic_out.writeline("LINE\n")
        basic_out.writeline("LINE 2\n")

        subtask_out.writeline("LINE\n")

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        assert_lines(
            log_content,
            "stdout  | main    | STDOUT\n",
            "stdout  | main    | STDOUT 2\n",
            "stderr  | main    | STDERR\n",
            "stderr  | main    | STDERR 2\n",
            "logging | main    | INFO info\n",
            "logging | main    | WARNING warning\n",
            "logging | main    | ERROR error\n",
            "writer  | main    | WRITER\n",
            "writer  | main    | WRITER 2\n",
            "lwriter | main    | LINE\n",
            "lwriter | main    | LINE 2\n",
            "basic   | main    | LINE\n",
            "basic   | main    | LINE 2\n",
            "basic   | subtask | LINE\n",
        )

    def test_logging_exception(self, log, subject):
        logging_out = subject.out("logging")

        # it raises logs unhandled exceptions
        exception = Exception("exception")

        with pytest.raises(Exception) as exc:
            with logging_out.redirect_logging():
                raise exception

        # make sure it let the exception through
        assert exc.value is exception

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        # make sure the exception is logged
        assert "logging | main   | ERROR exception" in log_content
