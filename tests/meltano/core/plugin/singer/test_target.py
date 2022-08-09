from __future__ import annotations

import pytest

from meltano.core.job import Job, Payload
from meltano.core.plugin import PluginType
from meltano.core.project_plugins_service import PluginAlreadyAddedException


class TestSingerTarget:
    @pytest.fixture
    def subject(self, project_add_service):
        try:
            return project_add_service.add(PluginType.LOADERS, "target-mock")
        except PluginAlreadyAddedException as err:
            return err.plugin

    @pytest.mark.asyncio
    async def test_exec_args(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        async with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

    @pytest.mark.asyncio
    async def test_setup_bookmark_writer(
        self, subject, session, plugin_invoker_factory, elt_context_builder
    ):

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
            .with_full_refresh(True)
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
