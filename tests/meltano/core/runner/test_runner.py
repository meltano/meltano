import pytest
import os
import json
from asynctest import CoroutineMock

from unittest import mock
from meltano.core.job import Job, State
from meltano.core.plugin import Plugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.singer import SingerTap, SingerTarget
from meltano.core.runner.singer import SingerRunner, SingerPayload
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
    def subject(self, session, mkdtemp, project):
        tap_config_dir = mkdtemp()
        target_config_dir = mkdtemp()

        create_plugin_files(tap_config_dir, TAP)
        create_plugin_files(target_config_dir, TARGET)

        Job(
            job_id=TEST_JOB_ID,
            state=State.SUCCESS,
            payload_flags=SingerPayload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(
            project,
            TEST_JOB_ID,
            tap_config_dir=tap_config_dir,
            target_config_dir=target_config_dir,
        )

    @pytest.fixture()
    def process_mock_factory(self):
        def _factory(name):
            process_mock = mock.Mock()
            process_mock.name = name
            process_mock.wait = CoroutineMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def tap_process(self, process_mock_factory):
        tap = process_mock_factory(TAP)
        tap.stdout.readline = CoroutineMock(return_value="{}")
        return tap

    @pytest.fixture()
    def target_process(self, process_mock_factory):
        target = process_mock_factory(TARGET)
        return target

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

    @pytest.mark.asyncio
    async def test_invoke(self, subject, tap_process, target_process):
        tap_invoker = PluginInvoker(
            subject.project, TAP, config_dir=subject.tap_config_dir
        )
        target_invoker = PluginInvoker(
            subject.project, TARGET, config_dir=subject.target_config_dir
        )

        # call prepare beforehand
        subject.prepare(tap_invoker, target_invoker)

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))

        with mock.patch.object(
            SingerRunner, "bookmark", new=CoroutineMock()
        ), mock.patch.object(
            PluginInvoker, "invoke_async", new=invoke_async
        ) as invoke_async:
            # async method
            await subject.invoke(tap_invoker, target_invoker)

            # correct bins are called
            assert invoke_async.awaited_with(tap_invoker)
            assert invoke_async.awaited_with(target_invoker)

            tap_process.wait.assert_awaited()
            target_process.wait.assert_awaited()

    @pytest.mark.asyncio
    async def test_bookmark(self, subject, session, tap_process, target_process):
        lines = (
            b'{"type": "STATE", "value": {"line": 1}}\n',
            b'{"type": "STATE", "value": {"line": 2}}\n',
            b'{"type": "STATE", "value": {"line": 3}}\n',
        )

        # testing with a real subprocess proved to be pretty
        # complicated.
        target_process.stdout = mock.MagicMock()
        target_process.stdout.at_eof.side_effect = (False, False, False, True)
        target_process.stdout.readline = CoroutineMock(side_effect=lines)

        with subject.job.run(session):
            await subject.bookmark(target_process.stdout)

        # assert the STATE's `value` was saved
        assert subject.job.payload["singer_state"] == {"line": 3}

        # test the restore
        tap_invoker = PluginInvoker(subject.project, TAP)
        subject.restore_bookmark(session, tap_invoker)
        state_json = json.dumps(subject.job.payload["singer_state"])
        assert tap_invoker.files["state"].exists()
        assert tap_invoker.files["state"].open().read() == state_json
