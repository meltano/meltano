import os
from unittest import mock

import dotenv
import pytest
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.venv_service import VirtualEnv


class TestPluginInvoker:
    def test_env(self, project, tap, session, plugin_invoker_factory):
        project.dotenv.touch()
        dotenv.set_key(project.dotenv, "DUMMY_ENV_VAR", "from_dotenv")
        dotenv.set_key(project.dotenv, "TAP_MOCK_TEST", "from_dotenv")

        subject = plugin_invoker_factory(tap)
        with subject.prepared(session):
            env = subject.env()

        # .env
        assert env["DUMMY_ENV_VAR"] == "from_dotenv"

        # Project env
        assert env["MELTANO_PROJECT_ROOT"] == str(project.root)

        # Project settings
        assert env["MELTANO_CLI_LOG_LEVEL"] == "info"

        # Plugin info
        assert env["MELTANO_EXTRACTOR_NAME"] == tap.name

        # Plugin settings
        assert env["MELTANO_EXTRACT_TEST"] == env["TAP_MOCK_TEST"] == "from_dotenv"
        assert env["MELTANO_EXTRACT__SELECT"] == env["TAP_MOCK__SELECT"] == '["*.*"]'

        # Plugin execution environment
        venv = VirtualEnv(project.venvs_dir(tap.type, tap.name))
        assert env["VIRTUAL_ENV"] == str(venv.root)
        assert env["PATH"].startswith(str(venv.bin_dir))
        assert "PYTHONPATH" not in env
