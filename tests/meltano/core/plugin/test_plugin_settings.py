import pytest
from sqlalchemy.orm.session import make_transient

from meltano.core.plugin.setting import PluginSetting


def test_create(session):
    setting = PluginSetting(name="api_key.test.test",
                            namespace="gitlab",
                            value="C4F3C4F3",
                            enabled=True) # TODO: helper to autoenabled on change

    session.add(setting)
    session.commit()

    fetched = session.query(PluginSetting).first()
    assert(setting == fetched)
    assert(setting.env == "GITLAB_API_KEY__TEST__TEST")


def test_create_env(session):
    setting = PluginSetting(env="THIS_IS_A_TEST",
                            name="api_key",
                            namespace="gitlab",
                            value="C4F3C4F3",
                            enabled=True) # TODO: helper to autoenabled on change

    assert setting.env == "THIS_IS_A_TEST"
    session.add(setting)
    session.commit()


def test_create_file(session):
    setting = PluginSetting(name="file:///source_schema/test.cfg",
                            namespace="test",
                            value="",
                            enabled=True)

    session.add(setting)
    session.commit()
