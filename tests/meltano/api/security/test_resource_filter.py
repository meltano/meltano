import pytest
from flask import appcontext_pushed, g
from flask_login import current_user
from flask_principal import Identity, Need, Permission
from meltano.api.security.auth import ResourcePermission
from meltano.api.security.resource_filter import ResourceFilter, TopicFilter
from meltano.core.m5o.m5oc_file import M5ocFile


@pytest.fixture
def identity(app):
    identity = Identity("test")

    def handler(sender):
        g.identity = identity

    with appcontext_pushed.connected_to(handler, app):
        yield identity


class TestResourcePermission:
    def test_allows(self, identity):
        resource_need = Need("view:design", "*")
        identity.provides.add(resource_need)

        item_need = Need("view:design", "finance")
        assert ResourcePermission(item_need).allows(identity)

    def test_allows_reject(self, identity):
        item_need = Need("view:design", "finance")
        assert not ResourcePermission(item_need).allows(identity)


class TestTopicFilter:
    @pytest.fixture
    def subject(self):
        return TopicFilter()

    @pytest.fixture(scope="class", autouse=True)
    def compile_models(self, add_model, project_compiler):
        project_compiler.compile()

    def test_filter(self, project, identity, app):
        identity.provides.add(Need("view:topic", "*"))
        identity.provides.add(Need("view:design", "*"))

        path = project.run_dir("models", "model-carbon-intensity", "carbon.topic.m5oc")
        m5o_file = M5ocFile.load(path)
        topic_filter = TopicFilter()

        with app.app_context():
            scoped = list(topic_filter.filter("view:topic", [m5o_file.content]))

        assert len(scoped[0]["designs"]) == 1
