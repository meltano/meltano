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

    def test_exec_args(self, subject, session, plugin_invoker_factory):
        invoker = plugin_invoker_factory(subject)
        with invoker.prepared(session):
            assert subject.exec_args(invoker) == ["--config", invoker.files["config"]]

    def test_setup_bookmark_writer(
        self, subject, session, plugin_invoker_factory, elt_context_builder
    ):

        job = Job(job_id="pytest_test_runner")

        elt_context = (
            elt_context_builder.with_session(session)
            .with_loader(subject.name)
            .with_job(job)
            .context()
        )
        invoker = plugin_invoker_factory(subject, context=elt_context)
        with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert len(invoker.output_handlers.get(invoker.STD_OUT)) == 1
            assert (
                invoker.output_handlers.get(invoker.STD_OUT)[0].payload_flag
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
        with invoker.prepared(session):
            subject.setup_bookmark_writer(invoker)
            assert len(invoker.output_handlers.get(invoker.STD_OUT)) == 1
            assert (
                invoker.output_handlers.get(invoker.STD_OUT)[0].payload_flag
                is Payload.INCOMPLETE_STATE
            )
