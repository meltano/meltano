import pytest
import os
import json
from asynctest import CoroutineMock

from unittest import mock
from meltano.core.job import Job, State
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.plugin import Plugin, PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin.factory import plugin_factory
from meltano.core.plugin.singer import SingerTap, SingerTarget
from meltano.core.runner.singer import SingerRunner, SingerPayload
from pathlib import Path


TEST_JOB_ID = "test_job"


class AnyInstanceOf:
    def __init__(self, cls):
        self._cls = cls

    def __eq__(self, other):
        return isinstance(other, self._cls)

    def __repr__(self):
        return f"<Any({self._cls}>"


def create_plugin_files(config_dir: Path, plugin: Plugin):
    for file in plugin.config_files.values():
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


class TestSingerRunner:
    @pytest.fixture()
    def elt_context(self, project, session, tap, target, elt_context_builder):
        job = Job(job_id="pytest_test_runner")

        return (
            elt_context_builder.with_extractor(tap.name)
            .with_job(job)
            .with_loader(target.name)
            .context(session)
        )

    @pytest.fixture()
    def tap_config_dir(self, mkdtemp, elt_context):
        tap_config_dir = mkdtemp()
        create_plugin_files(tap_config_dir, elt_context.extractor.install)
        return tap_config_dir

    @pytest.fixture()
    def target_config_dir(self, mkdtemp, elt_context):
        target_config_dir = mkdtemp()
        create_plugin_files(target_config_dir, elt_context.loader.install)
        return target_config_dir

    @pytest.fixture()
    def subject(self, session, elt_context):
        Job(
            job_id=TEST_JOB_ID,
            state=State.SUCCESS,
            payload_flags=SingerPayload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(elt_context)

    @pytest.fixture()
    def process_mock_factory(self):
        def _factory(name):
            process_mock = mock.Mock()
            process_mock.name = name
            process_mock.wait = CoroutineMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def tap_process(self, process_mock_factory, tap):
        tap = process_mock_factory(tap)
        tap.stdout.readline = CoroutineMock(return_value="{}")
        return tap

    @pytest.fixture()
    def target_process(self, process_mock_factory, target):
        target = process_mock_factory(target)
        return target

    def test_prepare_job(
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        tap,
        target,
        plugin_invoker_factory,
    ):
        tap_invoker = plugin_invoker_factory(
            tap, config_dir=tap_config_dir, prepare_with_session=session
        )
        target_invoker = plugin_invoker_factory(
            target, config_dir=target_config_dir, prepare_with_session=session
        )

        for f in tap.config_files.values():
            assert tap_config_dir.joinpath(f).exists()

        for f in target.config_files.values():
            assert target_config_dir.joinpath(f).exists()

    @pytest.mark.asyncio
    async def test_invoke(
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        tap,
        target,
        tap_process,
        target_process,
        plugin_invoker_factory,
    ):
        tap_invoker = plugin_invoker_factory(
            tap, config_dir=tap_config_dir, prepare_with_session=session
        )
        target_invoker = plugin_invoker_factory(
            target, config_dir=target_config_dir, prepare_with_session=session
        )

        invoke_async = CoroutineMock(side_effect=(tap_process, target_process))

        # fmt: off
        with mock.patch.object(SingerRunner, "bookmark", new=CoroutineMock()), \
          mock.patch.object(PluginInvoker, "invoke_async", new=invoke_async) as invoke_async:
            # async method
            await subject.invoke(tap_invoker, target_invoker)

            # correct bins are called
            assert invoke_async.awaited_with(tap_invoker)
            assert invoke_async.awaited_with(target_invoker)

            tap_process.wait.assert_awaited()
            target_process.wait.assert_awaited()
        # fmt: on

    @pytest.mark.asyncio
    async def test_bookmark(
        self, subject, session, tap, tap_process, target_process, plugin_invoker_factory
    ):
        lines = (b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n')

        # testing with a real subprocess proved to be pretty
        # complicated.
        target_process.stdout = mock.MagicMock()
        target_process.stdout.at_eof.side_effect = (False, False, False, True)
        target_process.stdout.readline = CoroutineMock(side_effect=lines)

        with subject.context.job.run(session):
            await subject.bookmark(target_process.stdout)

        # assert the STATE's `value` was saved
        assert subject.context.job.payload["singer_state"] == {"line": 3}

        # test the restore
        tap_invoker = plugin_invoker_factory(tap)
        subject.restore_bookmark(session, tap_invoker)
        state_json = json.dumps(subject.context.job.payload["singer_state"])
        assert tap_invoker.files["state"].exists()
        assert tap_invoker.files["state"].open().read() == state_json

    def test_run(self, subject, session):
        async def invoke_mock(*args):
            pass

        # fmt: off
        with mock.patch.object(SingerRunner, "restore_bookmark") as restore_bookmark, \
          mock.patch.object(SingerRunner, "invoke", side_effect=invoke_mock) as invoke:
            subject.run(session, dry_run=True)

            assert not restore_bookmark.called
            assert not invoke.called

            subject.run(session)
            AnyPluginInvoker = AnyInstanceOf(PluginInvoker)

            restore_bookmark.assert_called_once_with(session, AnyPluginInvoker)
            invoke.assert_called_once_with(AnyPluginInvoker, AnyPluginInvoker)
        # fmt: on
