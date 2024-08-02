from __future__ import annotations

import errno
import os
from typing import NoReturn  # noqa: ICN003

import mock
import pytest
import yaml
from sqlalchemy.exc import OperationalError

from meltano.core.plugin_remove_service import PluginRemoveService


class TestPluginRemoveService:
    @pytest.fixture()
    def subject(self, project):
        return PluginRemoveService(project)

    @pytest.fixture()
    def add(self, subject: PluginRemoveService) -> None:
        with subject.project.meltanofile.open("w") as meltano_yml:
            meltano_yml.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                                },
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
                                },
                            ],
                        },
                    },
                ),
            )

    @pytest.fixture()
    def install(self, subject: PluginRemoveService) -> None:
        tap_gitlab_installation = subject.project.meltano_dir().joinpath(
            "extractors",
            "tap-gitlab",
        )
        target_csv_installation = subject.project.meltano_dir().joinpath(
            "loaders",
            "target-csv",
        )
        tap_gitlab_installation.mkdir(parents=True, exist_ok=True)
        target_csv_installation.mkdir(parents=True, exist_ok=True)

    @pytest.fixture()
    def lock(self, subject: PluginRemoveService) -> None:
        tap_gitlab_lockfile = subject.project.plugin_lock_path(
            "extractors",
            "tap-gitlab",
            variant_name="meltanolabs",
        )
        target_csv_lockfile = subject.project.plugin_lock_path(
            "loaders",
            "target-csv",
            variant_name="hotgluexyz",
        )
        tap_gitlab_lockfile.touch()
        target_csv_lockfile.touch()

    def test_default_init_should_not_fail(self, subject) -> None:
        assert subject

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove(self, subject: PluginRemoveService) -> None:
        plugins = list(subject.project.plugins.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == total_plugins

        for plugin in plugins:
            # check removed from meltano.yml
            with subject.project.meltanofile.open() as meltanofile:
                meltano_yml = yaml.safe_load(meltanofile)

                with pytest.raises(KeyError):
                    meltano_yml[plugin.type, plugin.name]

            # check removed installation
            path = subject.project.meltano_dir().joinpath(plugin.type, plugin.name)
            assert not path.exists()

            # check removed lock files
            lock_file_paths = list(
                subject.project.root_plugins_dir(plugin.type).glob(
                    f"{plugin.name}*.lock",
                ),
            )
            assert all(not path.exists() for path in lock_file_paths)

    def test_remove_not_added_or_installed(self, subject: PluginRemoveService) -> None:
        plugins = list(subject.project.plugins.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_db_error(self, subject: PluginRemoveService) -> None:
        plugins = list(subject.project.plugins.plugins())

        with mock.patch(
            "meltano.core.plugin_location_remove.PluginSettingsService.reset",
        ) as reset:
            reset.side_effect = OperationalError(
                "DELETE FROM plugin_settings WHERE plugin_settings.namespace = ?",
                ("extractors.tap-csv.default"),
                "attempt to write a readonly database",
            )
            removed_plugins, _ = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_meltano_yml_error(self, subject: PluginRemoveService) -> None:
        def raise_permissionerror(filename) -> NoReturn:
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.project.plugins.plugins())
        with mock.patch.object(
            subject.project.plugins,
            "remove_from_file",
            side_effect=raise_permissionerror,
        ):
            removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_installation_error(self, subject: PluginRemoveService) -> None:
        def raise_permissionerror(filename) -> NoReturn:
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.project.plugins.plugins())

        with mock.patch("meltano.core.plugin_location_remove.shutil.rmtree") as rmtree:
            rmtree.side_effect = raise_permissionerror
            removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install")
    def test_remove_lockfile_not_found(self, subject: PluginRemoveService) -> None:
        plugins = list(subject.project.plugins.plugins())
        removed_plugins, _ = subject.remove_plugins(plugins)

        assert removed_plugins == 0
