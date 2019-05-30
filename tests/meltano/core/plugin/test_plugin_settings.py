import pytest
from meltano.core.plugin.setting import PluginSetting


def test_create(session):
    setting = PluginSetting(key="GITLAB_API_KEY",
                            name="gitlab_api_key",
                            plugin="tap-gitlab",
                            value="C4F3C4F3",
                            enabled=True) # TODO: helper to autoenabled on change

    session.add(setting)
    session.commit()

    fetched = session.query(PluginSetting).first()
    assert(setting == fetched)


def test_create_file(session):
    setting = PluginSetting(key="SOURCE_SCHEMA",
                            name="file:///source_schema/test.cfg",
                            plugin="test",
                            value="",
                            enabled=True)

    session.add(setting)
    session.commit()
