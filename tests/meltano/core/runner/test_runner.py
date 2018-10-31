import pytest
import os
import json

from unittest import mock
from meltano.core.job import Job, State
from meltano.core.plugin import Plugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer import SingerTap, SingerTarget
from meltano.core.runner.singer import SingerRunner
from pathlib import Path


TEST_JOB_ID = "test_job"
TAP = SingerTap("tap-test")
TARGET = SingerTarget("target-test")


def create_plugin_files(config_dir: Path, plugin: Plugin):
    for file in plugin.config_files.values():
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


class TestSingerRunner:
    @pytest.fixture()
    def subject(self, db_setup, mkdtemp, project):
        tap_config_dir = mkdtemp()
        target_config_dir = mkdtemp()

        create_plugin_files(tap_config_dir, TAP)
        create_plugin_files(target_config_dir, TARGET)

        Job(
            elt_uri=TEST_JOB_ID,
            state=State.SUCCESS,
            payload={"singer_state": {"bookmarks": []}},
        ).save()

        return SingerRunner(
            project,
            TEST_JOB_ID,
            tap_config_dir=tap_config_dir,
            target_config_dir=target_config_dir,
        )

    def test_prepare_job(self, subject):
        tap_invoker = PluginInvoker(
            subject.project, TAP, config_dir=subject.tap_config_dir
        )
        target_invoker = PluginInvoker(
            subject.project, TARGET, config_dir=subject.target_config_dir
        )

        subject.prepare(tap_invoker, target_invoker)

        for f in TAP.config_files.values():
            assert subject.tap_config_dir.joinpath(f).exists()

        for f in TARGET.config_files.values():
            assert subject.target_config_dir.joinpath(f).exists()

    @mock.patch("subprocess.Popen")
    def test_invoke(self, Popen, subject):
        called_bins = []
        tap_invoker = PluginInvoker(
            subject.project, TAP, config_dir=subject.tap_config_dir
        )
        target_invoker = PluginInvoker(
            subject.project, TARGET, config_dir=subject.target_config_dir
        )

        # call prepare beforehand
        subject.prepare(tap_invoker, target_invoker)

        def Popen_record_bin(cmd, *args, **kwargs):
            called_bins.append(list(cmd)[0])
            return mock.DEFAULT

        # mock Popen and make sure the paths are valid
        process_mock = mock.Mock()
        process_mock.wait.return_value = 0
        Popen.return_value = process_mock
        Popen.side_effect = Popen_record_bin

        subject.invoke(tap_invoker, target_invoker)

        tap_bin = str(tap_invoker.exec_path())
        target_bin = str(target_invoker.exec_path())

        # correct bins are called
        assert called_bins == [target_bin, "tee", tap_bin]

        # pipeline is closed
        assert process_mock.stdin.close.call_count == 3
        assert process_mock.wait.call_count == 3

    def test_bookmark(self, subject):
        target_invoker = PluginInvoker(subject.project, TARGET)
        # bookmark
        with target_invoker.files["state"].open("w") as state:
            state.write('{"line": 1}\n')
            state.write('{"line": 2}\n')

        with subject.job.run():
            subject.bookmark(target_invoker)

        assert subject.job.payload["singer_state"]["line"] == 2

        # restore
        tap_invoker = PluginInvoker(subject.project, TAP)
        subject.restore_bookmark(tap_invoker)
        state_json = json.dumps(subject.job.payload["singer_state"])
        assert tap_invoker.files["state"].exists()
        assert tap_invoker.files["state"].open().read() == state_json
