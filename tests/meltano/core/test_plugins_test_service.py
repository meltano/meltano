import json
from unittest.mock import Mock, patch

import pytest
from meltano.core.plugin_test_service import ExtractorTestService

MOCK_STATE_MESSAGE = json.dumps({"type": "STATE"})
MOCK_RECORD_MESSAGE = json.dumps({"type": "RECORD"})


class TestExtractorTestService:
    @pytest.fixture(autouse=True)
    @patch("meltano.core.plugin_test_service.PluginInvoker")
    def setup(self, mock_invoker):
        self.mock_invoke = Mock()
        self.mock_invoker = mock_invoker
        self.mock_invoker.invoke.return_value = self.mock_invoke

    def test_validate_success(self):
        self.mock_invoke.poll.return_value = None
        self.mock_invoke.stdout.readline.return_value = MOCK_RECORD_MESSAGE

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail is None

    def test_validate_success_ignore_non_json(self):
        mock_output = [
            "Not JSON",
            MOCK_RECORD_MESSAGE,
        ]

        self.mock_invoke.poll.return_value = None
        self.mock_invoke.stdout.readline.side_effect = mock_output

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail is None

    def test_validate_success_ignore_non_record_msg(self):
        mock_output = [
            json.dumps({"key": "value"}),
            MOCK_RECORD_MESSAGE,
        ]

        self.mock_invoke.stdout.readline.side_effect = mock_output
        self.mock_invoke.poll.return_value = None

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail is None

    def test_validate_success_stop_after_record_msg(self):
        mock_output = [
            MOCK_STATE_MESSAGE,
            MOCK_RECORD_MESSAGE,
            MOCK_RECORD_MESSAGE,
        ]

        self.mock_invoke.stdout.readline.side_effect = mock_output
        self.mock_invoke.poll.return_value = None

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert is_valid
        assert detail is None

        first_record_message_index = mock_output.index(MOCK_RECORD_MESSAGE)
        assert (
            self.mock_invoke.stdout.readline.call_count
            == first_record_message_index + 1
        )

    def test_validate_failure_no_record_msg(self):
        mock_output = [MOCK_STATE_MESSAGE]

        self.mock_invoke.returncode = 0
        self.mock_invoke.stdout.readline.side_effect = mock_output
        self.mock_invoke.poll.side_effect = [None for _ in mock_output] + [
            self.mock_invoke.returncode
        ]

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert "No RECORD message received" in detail

    def test_validate_failure_subprocess_err(self):
        mock_output = [
            MOCK_STATE_MESSAGE,
            "A subprocess error occurred",
        ]

        self.mock_invoke.returncode = 1
        self.mock_invoke.stdout.readline.side_effect = mock_output
        self.mock_invoke.poll.side_effect = [None for _ in mock_output] + [
            self.mock_invoke.returncode
        ]

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert mock_output[-1] in detail

    def test_validate_failure_plugin_invoke_exception(self):
        mock_exception = Exception("An exception occurred on plugin invocation")
        self.mock_invoker.invoke.side_effect = mock_exception

        is_valid, detail = ExtractorTestService(self.mock_invoker).validate()

        assert not is_valid
        assert str(mock_exception) in detail
