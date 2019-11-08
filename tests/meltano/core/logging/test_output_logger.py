import pytest
import tempfile
import io
import logging
import sys
from pathlib import Path

from meltano.core.logging.output_logger import OutputLogger


class TestOutputLogger:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.TemporaryFile(mode="w+", dir=tmp_path)
        # return io.StringIO()

    def test_context(self, log):
        with OutputLogger(log) as logger:
            print("STDOUT")
            print("STDERR")
            logging.info("INFO")
            logging.warning("WARNING")
            logging.error("ERROR")

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        assert "STDOUT" in log_content
        assert "STDERR" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content

    def test_context_exception(self, log):
        # it raises logs unhandled exceptions
        exception = Exception("EXCEPTION")

        # fmt: off
        with pytest.raises(Exception) as exc, \
          OutputLogger(log):
            raise exception
        # fmt: on

        # make sure it let the exception through
        assert exc.value is exception

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        # make sure the exception is logged
        assert "EXCEPTION" in log_content
