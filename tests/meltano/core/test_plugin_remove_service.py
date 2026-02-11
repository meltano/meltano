from __future__ import annotations

import errno
import json
import os
import shutil
import typing as t
from unittest import mock

import pytest
import yaml
from sqlalchemy.exc import OperationalError

from meltano.core.plugin_remove_service import PluginRemoveService

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from meltano.core.plugin_location_remove import PluginLocationRemoveManager


class TestPluginRemoveService:
    @pytest.fixture
    def subject(self, project):
        return PluginRemoveService(project)

    @pytest.fixture
    def add(self, subject: PluginRemoveService) -> Generator[None, None, None]:
        with subject.project.meltanofile.open("r") as meltano_yml:
            original = yaml.safe_load(meltano_yml)

        with subject.project.meltanofile.open("w") as meltano_yml:
            meltano_yml.write(
                yaml.dump(
                    {
                        "plugins": {
                            "extractors": [
                                {
                                    "name": "tap-gitlab",
                                    "variant": "meltanolabs",
                                    "pip_url": "git+https://github.com/MeltanoLabs/tap-gitlab.git",
                                },
                            ],
                            "loaders": [
                                {
                                    "name": "target-csv",
                                    "variant": "meltanolabs",
                                    "pip_url": "git+https://github.com/MeltanoLabs/target-csv.git",
                                },
                            ],
                        },
                    },
                ),
            )

        yield

        with subject.project.meltanofile.open("w") as meltano_yml:
            meltano_yml.write(yaml.dump(original))

    @pytest.fixture
    def no_plugins(self, subject: PluginRemoveService) -> Generator[None, None, None]:
        with subject.project.meltanofile.open("r") as meltano_yml:
            original = yaml.safe_load(meltano_yml)

        with subject.project.meltanofile.open("w") as meltano_yml:
            meltano_yml.write(yaml.dump({"plugins": {}}))

        yield

        with subject.project.meltanofile.open("w") as meltano_yml:
            meltano_yml.write(yaml.dump(original))

    @pytest.fixture
    def install(self, subject: PluginRemoveService) -> Generator[None, None, None]:
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
        yield
        shutil.rmtree(tap_gitlab_installation, ignore_errors=True)
        shutil.rmtree(target_csv_installation, ignore_errors=True)

    @pytest.fixture
    def lock(self, subject: PluginRemoveService) -> Generator[None, None, None]:
        tap_gitlab_lockfile = subject.project.plugin_lock_path(
            "extractors",
            "tap-gitlab",
            variant_name="meltanolabs",
        )
        target_csv_lockfile = subject.project.plugin_lock_path(
            "loaders",
            "target-csv",
            variant_name="meltanolabs",
        )
        with tap_gitlab_lockfile.open("w") as f:
            json.dump(
                {
                    "plugin_type": "extractors",
                    "name": "tap-gitlab",
                    "namespace": "tap_gitlab",
                    "variant": "meltanolabs",
                },
                f,
            )

        with target_csv_lockfile.open("w") as f:
            json.dump(
                {
                    "plugin_type": "loaders",
                    "name": "target-csv",
                    "namespace": "target_csv",
                    "variant": "meltanolabs",
                },
                f,
            )
        yield
        tap_gitlab_lockfile.unlink(missing_ok=True)
        target_csv_lockfile.unlink(missing_ok=True)

    def test_default_init_should_not_fail(self, subject) -> None:
        assert subject

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()
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

    @pytest.mark.usefixtures("no_plugins")
    def test_remove_not_added_or_installed(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()
        plugins = list(subject.project.plugins.plugins())
        removed_plugins, total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == total_plugins == 0

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_db_error(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()
        plugins = list(subject.project.plugins.plugins())

        assert plugins

        errors = []

        def _collect_error(manager: PluginLocationRemoveManager) -> None:
            errors.append(manager.message)

        with mock.patch(
            "meltano.core.plugin_location_remove.PluginSettingsService.reset",
        ) as reset:
            reset.side_effect = OperationalError(
                "DELETE FROM plugin_settings WHERE plugin_settings.namespace = ?",
                ("extractors.tap-csv.default"),
                "attempt to write a readonly database",
            )
            removed_plugins, _ = subject.remove_plugins(
                plugins,
                removal_manager_status_cb=_collect_error,
            )

        assert removed_plugins == 0
        assert errors.count("attempt to write a readonly database") == len(plugins)

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_meltano_yml_error(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()

        def raise_permissionerror(filename) -> t.NoReturn:
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.project.plugins.plugins())
        with mock.patch.object(
            subject.project.plugins,
            "remove_from_file",
            side_effect=raise_permissionerror,
        ):
            removed_plugins, _total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install", "lock")
    def test_remove_installation_error(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()

        def raise_permissionerror(filename) -> t.NoReturn:
            raise OSError(errno.EACCES, os.strerror(errno.ENOENT), filename)

        plugins = list(subject.project.plugins.plugins())

        with mock.patch("meltano.core.plugin_location_remove.shutil.rmtree") as rmtree:
            rmtree.side_effect = raise_permissionerror
            removed_plugins, _total_plugins = subject.remove_plugins(plugins)

        assert removed_plugins == 0

    @pytest.mark.usefixtures("add", "install")
    def test_remove_lockfile_not_found(self, subject: PluginRemoveService) -> None:
        subject.project.refresh()
        plugins = list(subject.project.plugins.plugins(ensure_parent=False))
        removed_plugins, _ = subject.remove_plugins(plugins)

        assert removed_plugins == 0
