import pytest
import subprocess

from unittest import mock


class TestSingerTap:
    @pytest.fixture
    def subject(self, tap, config_service):
        return config_service.get_plugin(tap)

    def test_discovery(self, subject, plugin_invoker_factory):
        Popen_spec = mock.create_autospec(subprocess.Popen)

        handle = mock.Mock(returncode=0)
        handle.communicate.return_value = ("STDOUT", "STDERR")
        invoker = plugin_invoker_factory(subject)

        def mock_catalog(*args, **kwargs):
            # call the POpen spec to make sure it complies
            Popen_spec(*args, **kwargs)

            with invoker.files["catalog"].open("w") as catalog:
                # an empty catalog should be valid
                catalog.write("{}")

            return handle

        with mock.patch.object(
            invoker, "invoke", side_effect=mock_catalog
        ) as invoke_mock:
            subject.run_discovery(invoker)

            assert invoke_mock.called
