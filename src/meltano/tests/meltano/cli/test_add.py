from __future__ import annotations

import os
import platform
import shutil

import mock
import pytest
import yaml

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin import PluginRef, PluginType, Variant
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.project import Project
from meltano.core.project_init_service import ProjectInitService


class TestCliAdd:
    @pytest.fixture(autouse=True)
    def patch_hub(self, meltano_hub_service: MeltanoHubService):
        with mock.patch(
            "meltano.core.project_plugins_service.MeltanoHubService",
            return_value=meltano_hub_service,
        ):
            yield

    @pytest.fixture
    def reset_project_context(
        self, project: Project, project_init_service: ProjectInitService
    ):
        shutil.rmtree(".", ignore_errors=True)
        project_init_service.create_files(project)

    @pytest.mark.order(0)
    @pytest.mark.parametrize(
        "plugin_type,plugin_name,default_variant,required_plugin_refs",
        [
            (PluginType.EXTRACTORS, "tap-carbon-intensity", "meltano", []),
            (PluginType.LOADERS, "target-sqlite", "meltanolabs", []),
            (PluginType.TRANSFORMS, "tap-carbon-intensity", "meltano", []),
            (
                PluginType.ORCHESTRATORS,
                "airflow",
                Variant.ORIGINAL_NAME,
                [PluginRef(PluginType.FILES, "airflow")],
            ),
        ],
        ids=[
            "single-extractor",
            "single-loader",
            "transform-and-related",
            "orchestrator-and-required",
        ],
    )
    def test_add(
        self,
        plugin_type,
        plugin_name,
        default_variant,
        required_plugin_refs,
        project,
        cli_runner,
        project_plugins_service,
        meltano_hub_service,
    ):
        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project_plugins_service.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", plugin_type.singular, plugin_name])

            if plugin_type is PluginType.TRANSFORMS:
                assert res.exit_code == 1, res.stdout
                assert isinstance(res.exception, CliError)
                assert "Dependencies not met:" in str(res.exception)
            else:
                assert res.exit_code == 0, res.stdout
                assert f"Added {plugin_type.descriptor} '{plugin_name}'" in res.stdout

                plugin = project_plugins_service.find_plugin(plugin_name, plugin_type)
                assert plugin
                assert plugin.variant == default_variant

                plugins = [plugin]

                for required_plugin_ref in required_plugin_refs:
                    if (required_plugin_ref._type) == PluginType.FILES and (
                        required_plugin_ref.name == "dbt"
                    ):
                        # file bundles with no managed files are added but do not appear in meltano.yml
                        assert (
                            f"Adding required file bundle '{required_plugin_ref.name}'"
                            in res.stdout
                        )
                    else:
                        plugin = project_plugins_service.get_plugin(required_plugin_ref)
                        assert plugin

                        assert (
                            f"Added required {plugin.type.descriptor} '{plugin.name}'"
                            in res.stdout
                        )

                        plugins.append(plugin)

                install_plugin_mock.assert_called()

    @pytest.mark.order(1)
    def test_add_multiple(self, project, cli_runner, project_plugins_service):
        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            cli_runner.invoke(cli, ["add", "extractors", "tap-gitlab"])

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            res = cli_runner.invoke(
                cli, ["add", "extractors", "tap-gitlab", "tap-adwords", "tap-facebook"]
            )

            assert res.exit_code == 0, res.stdout
            assert (
                "Extractor 'tap-gitlab' already exists in your Meltano project"
                in res.stderr
            )
            assert "Added extractor 'tap-adwords'" in res.stdout
            assert "Added extractor 'tap-facebook'" in res.stdout

            tap_gitlab = project_plugins_service.find_plugin(
                "tap-gitlab", PluginType.EXTRACTORS
            )
            assert tap_gitlab
            tap_adwords = project_plugins_service.find_plugin(
                "tap-adwords", PluginType.EXTRACTORS
            )
            assert tap_adwords
            tap_facebook = project_plugins_service.find_plugin(
                "tap-facebook", PluginType.EXTRACTORS
            )
            assert tap_facebook

            install_plugin_mock.assert_called_once_with(
                project,
                [tap_gitlab, tap_adwords, tap_facebook],
                reason=PluginInstallReason.ADD,
            )

    @pytest.mark.order(2)
    def test_add_transform(self, project, cli_runner):
        # adding Transforms requires the legacy 'dbt' Transformer
        cli_runner.invoke(cli, ["add", "transformer", "dbt"])
        cli_runner.invoke(cli, ["install", "transformer", "dbt"])

        res = cli_runner.invoke(cli, ["add", "transform", "tap-google-analytics"])
        assert_cli_runner(res)

        with project.root_dir("transform/packages.yml").open() as packages_file:
            packages_yaml = yaml.safe_load(packages_file)

        with project.root_dir("transform/dbt_project.yml").open() as project_file:
            project_yaml = yaml.safe_load(project_file)

        assert {
            "git": "https://gitlab.com/meltano/dbt-tap-google-analytics.git",
            "revision": "config-version-2",
        } in packages_yaml["packages"]

        assert "tap_google_analytics" in project_yaml["models"]
        assert project_yaml["vars"]["tap_google_analytics"] == {
            "schema": "{{ env_var('DBT_SOURCE_SCHEMA', 'tap_google_analytics') }}"
        }

    def test_add_files_with_updates(
        self,
        project,
        cli_runner,
        project_plugins_service,
        plugin_settings_service_factory,
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )
        # if plugin is locked, we actually wouldn't expect it to update.
        # So we must remove lockfile
        shutil.rmtree("plugins/files", ignore_errors=True)

        result = cli_runner.invoke(cli, ["add", "files", "airflow"])
        output = result.stdout + result.stderr
        assert_cli_runner(result)

        # Plugin has been added to meltano.yml
        plugin = project_plugins_service.find_plugin("airflow", PluginType.FILES)
        assert plugin

        # Automatic updating is enabled
        plugin_settings_service = plugin_settings_service_factory(plugin)
        update_config = plugin_settings_service.get("_update")
        assert update_config["orchestrate/dags/meltano.py"] is True

        # File has been created
        assert "Created orchestrate/dags/meltano.py" in output

        file_path = project.root_dir("orchestrate/dags/meltano.py")
        assert file_path.is_file()

        # File has "managed" header
        assert (
            "This file is managed by the 'airflow' file bundle" in file_path.read_text()
        )

    def test_add_files_without_updates(
        self, project, cli_runner, project_plugins_service
    ):
        result = cli_runner.invoke(cli, ["add", "files", "docker-compose"])
        output = result.stdout + result.stderr
        assert_cli_runner(result)

        # Plugin has not been added to meltano.yml
        with pytest.raises(PluginNotFoundError):
            project_plugins_service.find_plugin("docker-compose", PluginType.FILES)

        # File has been created
        assert "Created docker-compose.yml" in output

        file_path = project.root_dir("docker-compose.yml")
        assert file_path.is_file()

        # File does not have "managed" header
        assert "This file is managed" not in file_path.read_text()

    def test_add_files_that_already_exists(
        self, project, cli_runner, project_plugins_service
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )
        # dbt lockfile was created in an upstream test. Need to remove.
        shutil.rmtree(project.root_dir("plugins/files"), ignore_errors=True)
        project.root_dir("transform/dbt_project.yml").write_text("Exists!")
        result = cli_runner.invoke(cli, ["add", "files", "dbt"])
        output = result.stdout + result.stderr
        assert_cli_runner(result)

        assert (
            "File 'transform/dbt_project.yml' already exists, keeping both versions"
            in output
        )
        assert "Created transform/dbt_project (dbt).yml" in output
        assert project.root_dir("transform/dbt_project (dbt).yml").is_file()

    def test_add_missing(self, project, cli_runner, project_plugins_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert res.exception
        assert str(res.exception) == "Extractor 'tap-unknown' is not known to Meltano"

        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project_plugins_service.find_plugin("tap-unknown", PluginType.EXTRACTORS)

    @pytest.mark.xfail(reason="Uninstall not implemented yet.")
    def test_add_fails(self, project, cli_runner, project_plugins_service):
        result = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])
        output = result.stdout + result.stderr

        assert result.exit_code == 1, result.stdout
        assert "Failed to install plugin 'tap-mock'" in output
        assert result.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project_plugins_service.find_plugin("tap-mock", PluginType.EXTRACTORS)

    def test_add_variant(self, project, cli_runner, project_plugins_service):
        with mock.patch(
            "meltano.cli.add.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "mapper",
                    "mapper-mock",
                    "--variant",
                    "alternative",
                ],
            )
            assert_cli_runner(res)

            plugin = project_plugins_service.find_plugin(
                plugin_type=PluginType.MAPPERS, plugin_name="mapper-mock"
            )
            assert plugin.variant == "alternative"

    def test_add_inherited(
        self,
        project,
        tap,
        cli_runner,
        project_plugins_service,
        plugin_discovery_service,
    ):
        # Make sure tap-mock is not in the project as a project plugin
        project_plugins_service.remove_from_file(tap)

        with mock.patch(
            "meltano.cli.add.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True

            # Inheriting from a BasePlugin using --as
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "extractor",
                    "tap-mock",
                    "--as",
                    "tap-mock-inherited",
                ],
            )
            assert_cli_runner(res)
            assert "Inherit from:\ttap-mock, variant meltano (default)\n" in res.stdout

            inherited = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS, plugin_name="tap-mock-inherited"
            )
            assert inherited.inherit_from == "tap-mock"
            assert inherited.variant == "meltano"
            assert inherited.parent == plugin_discovery_service.find_base_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-mock",
                variant="meltano",
            )

            # Inheriting from a BasePlugin using --inherit-from and --variant
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "extractor",
                    "tap-mock--singer-io",
                    "--inherit-from",
                    "tap-mock",
                    "--variant",
                    "singer-io",
                ],
            )
            assert_cli_runner(res)
            assert (
                "Inherit from:\ttap-mock, variant singer-io (default)\n" in res.stdout
            )

            inherited_variant = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS, plugin_name="tap-mock--singer-io"
            )
            assert inherited_variant.inherit_from == "tap-mock"
            assert inherited_variant.variant == "singer-io"
            assert (
                inherited_variant.parent
                == plugin_discovery_service.find_base_plugin(
                    plugin_type=PluginType.EXTRACTORS,
                    plugin_name="tap-mock",
                    variant="singer-io",
                )
            )

            # Inheriting from a ProjectPlugin using --inherit-from
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "extractor",
                    "tap-mock-inception",
                    "--inherit-from",
                    "tap-mock-inherited",
                ],
            )
            assert_cli_runner(res)
            assert "Inherit from:\ttap-mock-inherited\n" in res.stdout

            inception = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS, plugin_name="tap-mock-inception"
            )
            assert inception.inherit_from == "tap-mock-inherited"
            assert inception.parent == inherited

            # Inheriting from a nonexistent plugin
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "extractor",
                    "tap-foo",
                    "--inherit-from",
                    "tap-bar",
                ],
            )
            assert res.exit_code == 1
            assert (
                "Could not find parent plugin for extractor 'tap-foo': Extractor 'tap-bar' is not known to Meltano"
                in str(res.exception)
            )

    def test_add_custom(self, project, cli_runner, project_plugins_service):
        pip_url = "-e path/to/tap-custom"
        executable = "tap-custom-bin"
        stdin = os.linesep.join(
            # namespace, pip_url, executable, capabilities, settings
            ["tap_custom", pip_url, executable, "foo,bar", "baz,qux"]
        )

        with mock.patch(
            "meltano.cli.add.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli, ["add", "--custom", "extractor", "tap-custom"], input=stdin
            )
            assert_cli_runner(res)

            plugin = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS, plugin_name="tap-custom"
            )
            assert plugin.name == "tap-custom"
            assert plugin.pip_url == pip_url

            plugin_def = plugin.custom_definition
            plugin_variant = plugin.custom_definition.variants[0]

            assert plugin_def.type == plugin.type
            assert plugin_def.name == plugin.name == "tap-custom"
            assert plugin_def.namespace == plugin.namespace == "tap_custom"

            assert plugin_variant.name is None

            assert plugin.pip_url == plugin_variant.pip_url == pip_url
            assert plugin.executable == plugin_variant.executable == executable
            assert plugin.capabilities == plugin_variant.capabilities == ["foo", "bar"]

            assert [stg.name for stg in plugin_variant.settings] == ["baz", "qux"]
            assert plugin.settings == plugin_variant.settings

            install_plugin_mock.assert_called_once_with(
                project, [plugin], reason=PluginInstallReason.ADD
            )

    def test_add_custom_no_install(self, project, cli_runner, project_plugins_service):
        executable = "tap-custom-noinstall"
        stdin = os.linesep.join(
            # namespace, pip_url, executable, capabilities, settings
            [
                "tap_custom_noinstall",
                "n",
                executable,
                "foo,bar",
                "baz,qux",
            ]
        )

        with mock.patch(
            "meltano.cli.add.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                ["add", "--custom", "extractor", executable],
                input=stdin,
            )
            assert_cli_runner(res)

            plugin: ProjectPlugin = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name=executable,
            )
            assert plugin.name == executable
            assert plugin.is_installable() is False
            assert plugin.is_invokable() is True
            assert plugin.pip_url is None

            plugin_def = plugin.custom_definition
            plugin_variant = plugin.custom_definition.variants[0]

            assert plugin_def.type == plugin.type
            assert plugin_def.name == plugin.name == executable

            assert plugin_variant.name is None

            assert plugin.pip_url is None and plugin_variant.pip_url is None
            assert plugin.executable == plugin_variant.executable == executable

            install_plugin_mock.assert_called_once_with(
                project, [plugin], reason=PluginInstallReason.ADD
            )

    def test_add_custom_variant(
        self, project, cli_runner, project_plugins_service, plugin_discovery_service
    ):
        with mock.patch(
            "meltano.cli.add.ProjectPluginsService",
            return_value=project_plugins_service,
        ), mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                [
                    "add",
                    "--custom",
                    "extractor",
                    "tap-custom-variant",
                    "--variant",
                    "personal",
                ],
            )
            assert_cli_runner(res)

            plugin = project_plugins_service.find_plugin(
                plugin_type=PluginType.EXTRACTORS, plugin_name="tap-custom-variant"
            )
            plugin_def = plugin.custom_definition
            plugin_variant = plugin_def.variants[0]

            assert plugin.variant == plugin_variant.name == "personal"

    @pytest.mark.parametrize(
        "plugin_type,plugin_name,default_variant,required_plugin_refs",
        [
            (PluginType.EXTRACTORS, "tap-carbon-intensity", "meltano", []),
            (PluginType.LOADERS, "target-sqlite", "meltanolabs", []),
            (PluginType.TRANSFORMS, "tap-carbon-intensity", "meltano", []),
            (
                PluginType.ORCHESTRATORS,
                "airflow",
                Variant.ORIGINAL_NAME,
                [PluginRef(PluginType.FILES, "airflow")],
            ),
        ],
        ids=[
            "single-extractor",
            "single-loader",
            "transform-and-related",
            "orchestrator-and-required",
        ],
    )
    def test_add_no_install(
        self,
        plugin_type,
        plugin_name,
        default_variant,
        required_plugin_refs,
        project,
        cli_runner,
        project_plugins_service,
        reset_project_context,
    ):
        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project_plugins_service.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli, ["add", plugin_type.singular, plugin_name, "--no-install"]
            )

            if plugin_type is PluginType.TRANSFORMS:
                assert res.exit_code == 1, res.stdout
                assert isinstance(res.exception, CliError)
                assert "Dependencies not met:" in str(res.exception)
            else:
                assert res.exit_code == 0, res.stdout
                assert f"Added {plugin_type.descriptor} '{plugin_name}'" in res.stdout

                plugin = project_plugins_service.find_plugin(plugin_name, plugin_type)
                assert plugin
                assert plugin.variant == default_variant

                # check plugin lock file is added
                plugins_dir = project.root_dir("plugins")
                assert plugins_dir.joinpath(
                    f"{plugin_type}/{plugin_name}--{default_variant}.lock"
                ).exists()

                for required_plugin_ref in required_plugin_refs:
                    if (required_plugin_ref._type) == PluginType.FILES and (
                        required_plugin_ref.name == "dbt"
                    ):
                        # file bundles with no managed files are added but do not appear in meltano.yml
                        assert (
                            f"Adding required file bundle '{required_plugin_ref.name}'"
                            in res.stdout
                        )
                    else:
                        plugin = project_plugins_service.get_plugin(required_plugin_ref)
                        assert plugin

                        assert (
                            f"Added required {plugin.type.descriptor} '{plugin.name}'"
                            in res.stdout
                        )

                    # check required plugin lock files are added
                    assert list(
                        plugins_dir.glob(
                            f"{required_plugin_ref._type}/{required_plugin_ref.name}--*.lock"
                        )
                    )

                install_plugin_mock.assert_not_called()
