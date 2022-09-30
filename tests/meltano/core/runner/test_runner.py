from __future__ import annotations

import os
from pathlib import Path

import mock
import pytest
from mock import AsyncMock

from meltano.core.job import Job, Payload, State
from meltano.core.logging.utils import capture_subprocess_output
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.runner.singer import SingerRunner

TEST_STATE_ID = "test_job"


class AnyInstanceOf:
    def __init__(self, target_cls):
        self.target_cls = target_cls

    def __eq__(self, other):
        return isinstance(other, self.target_cls)

    def __repr__(self):
        return f"<Any({self.target_cls}>"


def create_plugin_files(config_dir: Path, plugin: ProjectPlugin):
    for file in plugin.config_files.values():
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


class TestSingerRunner:
    @pytest.fixture()
    def elt_context(self, project, session, tap, target, elt_context_builder):
        job = Job(job_name="pytest_test_runner")

        return (
            elt_context_builder.with_session(session)
            .with_extractor(tap.name)
            .with_job(job)
            .with_loader(target.name)
            .context()
        )

    @pytest.fixture
    def tap_config_dir(self, tmp_path: Path, elt_context) -> Path:
        create_plugin_files(tmp_path, elt_context.extractor.plugin)
        return tmp_path

    @pytest.fixture
    def target_config_dir(self, tmp_path: Path, elt_context) -> Path:
        create_plugin_files(tmp_path, elt_context.loader.plugin)
        return tmp_path

    @pytest.fixture()
    def subject(self, session, elt_context):
        Job(
            job_name=TEST_STATE_ID,
            state=State.SUCCESS,
            payload_flags=Payload.STATE,
            payload={"singer_state": {"bookmarks": []}},
        ).save(session)

        return SingerRunner(elt_context)

    @pytest.fixture()
    def process_mock_factory(self):
        def _factory(name):
            process_mock = mock.Mock()
            process_mock.name = name
            process_mock.wait = AsyncMock(return_value=0)
            return process_mock

        return _factory

    @pytest.fixture()
    def tap_process(self, process_mock_factory, tap):
        tap = process_mock_factory(tap)
        tap.stdout.readline = AsyncMock(return_value="{}")
        return tap

    @pytest.fixture()
    def target_process(self, process_mock_factory, target):
        return process_mock_factory(target)

    @pytest.mark.asyncio
    async def test_prepare_job(
        self,
        session,
        subject,
        tap_config_dir,
        target_config_dir,
        tap,
        target,
        plugin_invoker_factory,
    ):
        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)

        async with tap_invoker.prepared(session):
            for name in tap.config_files.keys():
                assert tap_invoker.files[name].exists()

        assert not tap_invoker.files["config"].exists()

        async with target_invoker.prepared(session):
            for name in target.config_files.keys():
                assert target_invoker.files[name].exists()

        assert not target_invoker.files["config"].exists()

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
        tap_invoker = plugin_invoker_factory(tap, config_dir=tap_config_dir)
        target_invoker = plugin_invoker_factory(target, config_dir=target_config_dir)
        async with tap_invoker.prepared(  # noqa: WPS316
            session
        ), target_invoker.prepared(session):
            invoke_async = AsyncMock(side_effect=(tap_process, target_process))
            with mock.patch.object(
                PluginInvoker, "invoke_async", new=invoke_async
            ) as invoke_async:
                # async method
                await subject.invoke(tap_invoker, target_invoker, session)

                # correct bins are called
                assert await invoke_async.awaited_with(tap_invoker)
                assert await invoke_async.awaited_with(target_invoker)

                tap_process.wait.assert_awaited()
                target_process.wait.assert_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "full_refresh,select_filter,payload_flag",
        [
            (False, [], Payload.STATE),
            (True, [], Payload.STATE),
            (False, ["entity"], Payload.STATE),
            (True, ["entity"], Payload.INCOMPLETE_STATE),
        ],
    )
    async def test_bookmark(
        self,
        subject,
        session,
        target,
        target_config_dir,
        target_process,
        plugin_invoker_factory,
        full_refresh,
        select_filter,
        payload_flag,
        elt_context,
    ):
        lines = (b'{"line": 1}\n', b'{"line": 2}\n', b'{"line": 3}\n')

        # testing with a real subprocess proved to be pretty
        # complicated.
        target_process.stdout = mock.MagicMock()
        target_process.stdout.at_eof.side_effect = (False, False, False, True)
        target_process.stdout.readline = AsyncMock(side_effect=lines)

        subject.context.full_refresh = full_refresh
        subject.context.select_filter = select_filter

        target_invoker = plugin_invoker_factory(
            target, config_dir=target_config_dir, context=elt_context
        )

        async with subject.context.job.run(session):
            with mock.patch.object(
                session, "add", side_effect=session.add
            ) as add_mock, mock.patch.object(
                session, "commit", side_effect=session.commit
            ) as commit_mock:
                target.setup_bookmark_writer(target_invoker)
                bookmark_writer = target_invoker.output_handlers.get(
                    target_invoker.StdioSource.STDOUT
                )
                await capture_subprocess_output(target_process.stdout, *bookmark_writer)

            assert add_mock.call_count == 9
            assert commit_mock.call_count == 9

            # assert the STATE's `value` was saved
            job = subject.context.job
            assert job.payload["singer_state"] == {"line": 3}
            assert job.payload_flags == payload_flag

    @pytest.mark.asyncio
    async def test_run(self, subject):
        async def invoke_mock(*args, **kwargs):
            pass

        with mock.patch.object(
            SingerRunner, "invoke", side_effect=invoke_mock
        ) as invoke:
            subject.context.dry_run = True
            await subject.run()

            assert not invoke.called

            subject.context.dry_run = False
            await subject.run()
            AnyPluginInvoker = AnyInstanceOf(PluginInvoker)  # noqa: N806

            invoke.assert_called_once_with(
                AnyPluginInvoker,
                AnyPluginInvoker,
                extractor_log=None,
                loader_log=None,
                extractor_out=None,
                loader_out=None,
            )
