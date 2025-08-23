from __future__ import annotations

import json
import typing as t

import pytest

from meltano.core.job import Job, Payload
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer.target import BookmarkWriter
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.state_service import StateService

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.elt_context import ELTContextBuilder
    from meltano.core.plugin.singer.target import SingerTarget
    from meltano.core.project_add_service import ProjectAddService


class TestBookmarkWriter:
    @pytest.mark.parametrize(
        ("state_line", "expected_state", "writer_payload_flag"),
        (
            pytest.param(
                "test",
                {"singer_state": {"foo": "bar"}},
                Payload.STATE,
                id="invalid_state",
            ),
            pytest.param(
                '{"qux": "quux"}',
                {"singer_state": {"qux": "quux"}},
                Payload.STATE,
                id="valid_state",
            ),
            pytest.param(
                '{"qux": "quux"}',
                {"singer_state": {"foo": "bar", "qux": "quux"}},
                Payload.INCOMPLETE_STATE,
                id="valid_incomplete_state",
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_writeline(
        self,
        session: Session,
        state_line: str,
        expected_state: dict,
        writer_payload_flag: Payload,
    ) -> None:
        existing_state = {"singer_state": {"foo": "bar"}}
        state_service = StateService(session=session)

        job = Job(job_name="pytest_test_runner", payload=existing_state)
        job.save(session)
        state_service.add_state(job, json.dumps(existing_state))

        writer = BookmarkWriter(
            job,
            session,
            state_service=state_service,
            payload_flag=writer_payload_flag,
        )
        writer.writeline(state_line)

        assert state_service.get_state(job.job_name) == expected_state


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service: ProjectAddService):
        try:
            return project_add_service.add(PluginType.LOADERS, "target-mock")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.mark.asyncio
    async def test_exec_args(self, subject, session, plugin_invoker_factory) -> None:
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

    @pytest.mark.asyncio
    async def test_setup_bookmark_writer(
        self,
        subject: SingerTarget,
        session,
        plugin_invoker_factory,
        elt_context_builder: ELTContextBuilder,
    ) -> None:
        job = Job(job_name="pytest_test_runner")

        # test noop run outside of pipeline context
        invoker = plugin_invoker_factory(subject, context=None)
        async with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert invoker.output_handlers is None

        # test noop run with job but no session
        elt_context = (
            elt_context_builder.with_session(None)
            .with_loader(subject.name)
            .with_job(job)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)
        async with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert invoker.output_handlers is None

        # test noop run with session but no job
        elt_context = (
            elt_context_builder.with_session(session)
            .with_loader(subject.name)
            .with_job(None)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)
        async with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert invoker.output_handlers is None

        # test running inside of pipeline context
        elt_context = (
            elt_context_builder.with_session(session)
            .with_loader(subject.name)
            .with_job(job)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)
        async with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert len(invoker.output_handlers.get(invoker.StdioSource.STDOUT)) == 1
            assert (
                invoker.output_handlers.get(invoker.StdioSource.STDOUT)[0].payload_flag
                is Payload.STATE
            )

        # test w/ incomplete state (requires a filter and full refresh)
        elt_context = (
            elt_context_builder.with_session(session)
            .with_loader(subject.name)
            .with_job(job)
            .with_select_filter(["entity", "!other_entity"])
            .with_full_refresh(full_refresh=True)
            .context()
        )

        invoker = plugin_invoker_factory(subject, context=elt_context)
        async with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert len(invoker.output_handlers.get(invoker.StdioSource.STDOUT)) == 1
            assert (
                invoker.output_handlers.get(invoker.StdioSource.STDOUT)[0].payload_flag
                is Payload.INCOMPLETE_STATE
            )
