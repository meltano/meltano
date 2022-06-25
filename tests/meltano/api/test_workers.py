from unittest import mock

import pytest

from meltano.api.workers import UIAvailableWorker


class TestUIAvailableWorker:
    @pytest.fixture
    def subject(self, project):
        return UIAvailableWorker(project, open_browser=True)

    @mock.patch("time.sleep")  # don't wait for real
    @mock.patch("webbrowser.open")
    @mock.patch("requests.get")
    def test_open_browser(self, requests_get, webbrowser_open, sleep, subject):
        ERROR = mock.Mock(status_code=400)
        OK = mock.Mock(status_code=200)
        requests_get.side_effect = [ERROR, ERROR, OK]
        sleep.return_value = None

        subject.run()
        webbrowser_open.assert_called_with("http://localhost:5000")
        assert requests_get.call_count == sleep.call_count
