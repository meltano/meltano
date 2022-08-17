from __future__ import annotations

import errno
import os

import mock
import pytest
import yaml
from sqlalchemy.exc import OperationalError

from meltano.core.plugin_remove_service import PluginRemoveService


class TestPluginRemoveService:
    @pytest.fixture
    def subject(self, project):
        return PluginRemoveService(project)

    @pytest.fixture
    def add(self, subject: PluginRemoveService):
        with open(subject.project.meltanofile, "w") as meltano_yml:
            meltano_yml.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                                }
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                                }
                            ],
                        }
                    }
                )
            )

    @pytest.fixture
    def install(self, subject: PluginRemoveService):
        tap_gitlab_installation = subject.project.meltano_dir().joinpath(
            "extractors", "tap-gitlab"
        )
        target_csv_installation = subject.project.meltano_dir().joinpath(
            "loaders", "target-csv"
        )
        os.makedirs(tap_gitlab_installation, exist_ok=True)
        os.makedirs(target_csv_installation, exist_ok=True)

    @pytest.fixture
    def lock(self, subject: PluginRemoveService):
        tap_gitlab_lockfile = subject.project.plugin_lock_path(
            "extractors", "tap-gitlab", "meltanolabs"
        )
        target_csv_lockfile = subject.project.plugin_lock_path(
            "loaders", "target-csv", "hotgluexyz"
        )
        tap_gitlab_lockfile.touch()
        target_csv_lockfile.touch()

    def test_default_init_should_not_fail(self, subject):
        assert subject

    def test_remove(
        self,
        subject: PluginRemoveService,
        add,
        install,
        lock,
    ):
        plugins = list(subject.plugins_service.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == total_plugins

        for plugin in plugins:
            # check removed from meltano.yml
            with open(subject.project.meltanofile) as meltanofile:
                meltano_yml = yaml.safe_load(meltanofile)

                with pytest.raises(KeyError):
                    plugin_data = meltano_yml[plugin.type, plugin.name]
                    assert not plugin_data

            # check removed installation
            assert not os.path.exists(
                subject.project.meltano_dir().joinpath(plugin.type, plugin.name)
            )

            # check removed lock files
            lock_file_paths = list(
                subject.project.root_plugins_dir(plugin.type).glob(
                    f"{plugin.name}*.lock"
                )
            )
            assert all(not path.exists() for path in lock_file_paths)

    def test_remove_not_added_or_installed(self, subject: PluginRemoveService):
        plugins = list(subject.plugins_service.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    def test_remove_db_error(
        self,
        subject: PluginRemoveService,
        add,
        install,
        lock,
    ):
        plugins = list(subject.plugins_service.plugins())

        with mock.patch(
            "meltano.core.plugin_location_remove.PluginSettingsService.reset"
        ) as reset:
            reset.side_effect = OperationalError(
                "DELETE FROM plugin_settings WHERE plugin_settings.namespace = ?",
                ("extractors.tap-csv.default"),
                "attempt to write a readonly database",
            )
            removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    def test_remove_meltano_yml_error(
        self,
        subject: PluginRemoveService,
        add,
        install,
        lock,
    ):
        def raise_permissionerror(filename):
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.plugins_service.plugins())

        with mock.patch(
            "meltano.core.plugin_location_remove.ProjectPluginsService.remove_from_file"
        ) as remove_from_file:
            remove_from_file.side_effect = raise_permissionerror
            removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    def test_remove_installation_error(
        self,
        subject: PluginRemoveService,
        add,
        install,
        lock,
    ):
        def raise_permissionerror(filename):
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.plugins_service.plugins())

        with mock.patch("meltano.core.plugin_location_remove.shutil.rmtree") as rmtree:
            rmtree.side_effect = raise_permissionerror
            removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    def test_remove_lockfile_not_found(
        self,
        subject: PluginRemoveService,
        add,
        install,
    ):
        plugins = list(subject.plugins_service.plugins())
        removed_plugins, _ = subject.remove_plugins(plugins)

        assert removed_plugins == 0
