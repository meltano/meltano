from __future__ import annotations

import json
import os
import platform
import shutil
import typing as t
from pathlib import Path

import mock
import pytest
import yaml

from asserts import assert_cli_runner
from fixtures.cli import plugins_dir
from meltano.cli import cli
from meltano.cli.utils import CliError
from meltano.core.plugin import PluginRef, PluginType, Variant
from meltano.core.plugin.error import InvalidPluginDefinitionError, PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason

if t.TYPE_CHECKING:
    from click.testing import CliRunner

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

plugin_ref = plugins_dir / "extractors" / "tap-custom" / "test.yml"
fails_on_windows = pytest.mark.xfail(
    platform.system() == "Windows",
    reason="Fails on Windows: https://github.com/meltano/meltano/issues/3444",
)


class TestCliAdd:
    @pytest.mark.order(0)
    @pytest.mark.parametrize(
        ("plugin_type", "plugin_name", "default_variant", "required_plugin_refs"),
        (
            (PluginType.EXTRACTORS, "tap-carbon-intensity", "meltano", []),
            (PluginType.LOADERS, "target-sqlite", "meltanolabs", []),
            (PluginType.TRANSFORMS, "tap-carbon-intensity", "meltano", []),
            (
                PluginType.ORCHESTRATORS,
                "airflow",
                Variant.ORIGINAL_NAME,
                [PluginRef(PluginType.FILES, "airflow")],
            ),
        ),
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
        project: Project,
        cli_runner,
    ) -> None:
        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", plugin_type.singular, plugin_name])

            if plugin_type is PluginType.TRANSFORMS:
                assert res.exit_code == 1, res.stdout
                assert isinstance(res.exception, CliError)
                assert "Dependencies not met:" in str(res.exception)
            else:
                assert res.exit_code == 0, res.stdout
                assert f"Added {plugin_type.descriptor} '{plugin_name}'" in res.stdout

                plugin = project.plugins.find_plugin(plugin_name, plugin_type)
                assert plugin
                assert plugin.variant == default_variant

                plugins = [plugin]

                for required_plugin_ref in required_plugin_refs:
                    if (required_plugin_ref._type) == PluginType.FILES and (
                        required_plugin_ref.name == "dbt"
                    ):
                        # File bundles with no managed files are added but
                        # do not appear in meltano.yml
                        assert (
                            f"Adding required file bundle '{required_plugin_ref.name}'"
                            in res.stdout
                        )
                    else:
                        plugin = project.plugins.get_plugin(required_plugin_ref)
                        assert plugin

                        assert (
                            f"Added required {plugin.type.descriptor} '{plugin.name}'"
                            in res.stdout
                        )

                        plugins.append(plugin)

                install_plugin_mock.assert_called()

    @pytest.mark.order(1)
    def test_add_multiple(self, project: Project, cli_runner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            cli_runner.invoke(cli, ["add", "extractors", "tap-gitlab"])

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            res = cli_runner.invoke(
                cli,
                ["add", "extractors", "tap-gitlab", "tap-adwords", "tap-facebook"],
            )

            assert res.exit_code == 0, res.stdout
            assert (
                "Extractor 'tap-gitlab' already exists in your Meltano project"
                in res.stderr
            )
            assert "Added extractor 'tap-adwords'" in res.stdout
            assert "Added extractor 'tap-facebook'" in res.stdout

            tap_gitlab = project.plugins.find_plugin(
                "tap-gitlab",
                PluginType.EXTRACTORS,
            )
            assert tap_gitlab
            tap_adwords = project.plugins.find_plugin(
                "tap-adwords",
                PluginType.EXTRACTORS,
            )
            assert tap_adwords
            tap_facebook = project.plugins.find_plugin(
                "tap-facebook",
                PluginType.EXTRACTORS,
            )
            assert tap_facebook

            install_plugin_mock.assert_called_once_with(
                project,
                [tap_gitlab, tap_adwords, tap_facebook],
                reason=PluginInstallReason.ADD,
                force=False,
            )

    @pytest.mark.order(1)
    def test_add_different_variant(self, cli_runner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])
            assert res.exit_code == 0, res.stdout
            assert "Added extractor 'tap-mock" in res.stdout

            res = cli_runner.invoke(
                cli,
                ["add", "extractor", "tap-mock", "--variant", "singer-io"],
            )
            assert res.exit_code == 0, res.stdout
            assert (
                "Extractor 'tap-mock' already exists in your Meltano project"
                in res.stderr
            )
            assert "To switch from the current" in res.stdout
            assert "name: tap-mock" in res.stdout
            assert "variant: singer-io" in res.stdout

    @pytest.mark.order(2)
    def test_add_transform(self, project: Project, cli_runner) -> None:
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
            "schema": "{{ env_var('DBT_SOURCE_SCHEMA', 'tap_google_analytics') }}",
        }

    @fails_on_windows
    def test_add_files_with_updates(
        self,
        project: Project,
        cli_runner,
        plugin_settings_service_factory,
    ) -> None:
        # if plugin is locked, we actually wouldn't expect it to update.
        # So we must remove lockfile
        shutil.rmtree("plugins/files", ignore_errors=True)

        result = cli_runner.invoke(cli, ["add", "files", "airflow"])
        output = result.stdout + result.stderr
        assert_cli_runner(result)

        # Plugin has been added to meltano.yml
        plugin = project.plugins.find_plugin("airflow", PluginType.FILES)
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

    def test_add_files_without_updates(self, project: Project, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["add", "files", "docker-compose"])
        output = result.stdout + result.stderr
        assert_cli_runner(result)

        # Plugin has not been added to meltano.yml
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin("docker-compose", PluginType.FILES)

        # File has been created
        assert "Created docker-compose.yml" in output

        file_path = project.root_dir("docker-compose.yml")
        assert file_path.is_file()

        # File does not have "managed" header
        assert "This file is managed" not in file_path.read_text()

    @fails_on_windows
    def test_add_files_that_already_exists(self, project: Project, cli_runner) -> None:
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

    def test_add_missing(self, project: Project, cli_runner) -> None:
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert res.exception
        assert str(res.exception) == (
            "Extractor 'tap-unknown' is not known to Meltano. "
            "Check https://hub.meltano.com/ for available plugins."
        )

        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin("tap-unknown", PluginType.EXTRACTORS)

    @pytest.mark.xfail(reason="Uninstall not implemented yet.")
    def test_add_fails(self, project: Project, cli_runner) -> None:
        result = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])
        output = result.stdout + result.stderr

        assert result.exit_code == 1, result.stdout
        assert "Failed to install plugin 'tap-mock'" in output
        assert result.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin("tap-mock", PluginType.EXTRACTORS)

    def test_add_variant(self, project: Project, cli_runner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
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

            plugin = project.plugins.find_plugin(
                plugin_type=PluginType.MAPPERS,
                plugin_name="mapper-mock",
            )
            assert plugin.variant == "alternative"

    def test_add_inherited(
        self,
        project: Project,
        tap,
        cli_runner,
    ) -> None:
        # Make sure tap-mock is not in the project as a project plugin
        project.plugins.remove_from_file(tap)

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
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

            inherited = project.plugins.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-mock-inherited",
            )
            assert inherited.inherit_from == "tap-mock"
            assert inherited.variant == "meltano"
            assert inherited.parent == project.hub_service.find_base_plugin(
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
                "Inherit from:\ttap-mock, variant singer-io (deprecated)\n"
                in res.stdout
            )

            inherited_variant = project.plugins.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-mock--singer-io",
            )
            assert inherited_variant.inherit_from == "tap-mock"
            assert inherited_variant.variant == "singer-io"
            assert inherited_variant.parent == project.hub_service.find_base_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-mock",
                variant="singer-io",
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

            inception = project.plugins.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-mock-inception",
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
                "Could not find parent plugin for extractor 'tap-foo': "
                "Extractor 'tap-bar' is not known to Meltano"
            ) in str(res.exception)

    @pytest.mark.usefixtures("reset_project_context")
    def test_add_custom(self, project: Project, cli_runner) -> None:
        pip_url = "-e path/to/tap-custom"
        executable = "tap-custom-bin"
        stdin = os.linesep.join(
            # namespace, pip_url, executable, capabilities, settings
            ["tap_custom", pip_url, executable, "foo,bar", "baz,qux"],
        )

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                ["add", "--custom", "extractor", "tap-custom"],
                input=stdin,
            )
            assert_cli_runner(res)

            plugin = project.plugins.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-custom",
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
                project,
                [plugin],
                reason=PluginInstallReason.ADD,
                force=False,
            )

    def test_add_custom_no_install(self, project: Project, cli_runner) -> None:
        executable = "tap-custom-noinstall"
        stdin = os.linesep.join(
            # namespace, pip_url, executable, capabilities, settings
            [
                "tap_custom_noinstall",
                "n",
                executable,
                "foo,bar",
                "baz,qux",
            ],
        )

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                ["add", "--custom", "extractor", executable],
                input=stdin,
            )
            assert_cli_runner(res)

            plugin: ProjectPlugin = project.plugins.find_plugin(
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

            assert plugin.pip_url is None
            assert plugin_variant.pip_url is None
            assert plugin.executable == plugin_variant.executable == executable

            install_plugin_mock.assert_called_once_with(
                project,
                [plugin],
                reason=PluginInstallReason.ADD,
                force=False,
            )

    def test_add_custom_variant(self, project: Project, cli_runner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
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

            plugin = project.plugins.find_plugin(
                plugin_type=PluginType.EXTRACTORS,
                plugin_name="tap-custom-variant",
            )
            plugin_def = plugin.custom_definition
            plugin_variant = plugin_def.variants[0]

            assert plugin.variant == plugin_variant.name == "personal"

    @pytest.mark.parametrize(
        ("plugin_type", "plugin_name", "default_variant", "required_plugin_refs"),
        (
            (PluginType.EXTRACTORS, "tap-carbon-intensity", "meltano", []),
            (PluginType.LOADERS, "target-sqlite", "meltanolabs", []),
            (PluginType.TRANSFORMS, "tap-carbon-intensity", "meltano", []),
            (
                PluginType.ORCHESTRATORS,
                "airflow",
                Variant.ORIGINAL_NAME,
                [PluginRef(PluginType.FILES, "airflow")],
            ),
        ),
        ids=[
            "single-extractor",
            "single-loader",
            "transform-and-related",
            "orchestrator-and-required",
        ],
    )
    @pytest.mark.usefixtures("reset_project_context")
    def test_add_no_install(
        self,
        plugin_type,
        plugin_name,
        default_variant,
        required_plugin_refs,
        project: Project,
        cli_runner,
    ) -> None:
        # ensure the plugin is not present
        with pytest.raises(PluginNotFoundError):
            project.plugins.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                ["add", plugin_type.singular, plugin_name, "--no-install"],
            )

            if plugin_type is PluginType.TRANSFORMS:
                assert res.exit_code == 1, res.stdout
                assert isinstance(res.exception, CliError)
                assert "Dependencies not met:" in str(res.exception)
            else:
                assert res.exit_code == 0, res.stdout
                assert f"Added {plugin_type.descriptor} '{plugin_name}'" in res.stdout

                plugin = project.plugins.find_plugin(plugin_name, plugin_type)
                assert plugin
                assert plugin.variant == default_variant

                # check plugin lock file is added
                plugins_dir = project.root_dir("plugins")
                assert plugins_dir.joinpath(
                    f"{plugin_type}/{plugin_name}--{default_variant}.lock",
                ).exists()

                for required_plugin_ref in required_plugin_refs:
                    if (required_plugin_ref._type) == PluginType.FILES and (
                        required_plugin_ref.name == "dbt"
                    ):
                        # File bundles with no managed files are added but do
                        # not appear in meltano.yml
                        assert (
                            f"Adding required file bundle '{required_plugin_ref.name}'"
                            in res.stdout
                        )
                    else:
                        plugin = project.plugins.get_plugin(required_plugin_ref)
                        assert plugin

                        assert (
                            f"Added required {plugin.type.descriptor} '{plugin.name}'"
                            in res.stdout
                        )

                    # check required plugin lock files are added
                    assert list(
                        plugins_dir.glob(
                            f"{required_plugin_ref._type}/"
                            f"{required_plugin_ref.name}--*.lock",
                        ),
                    )

                install_plugin_mock.assert_not_called()

    @pytest.mark.parametrize(
        "ref",
        (
            plugin_ref,
            (
                "https://raw.githubusercontent.com/meltano/hub/main/_data/meltano/"
                f"{plugin_ref.relative_to(plugins_dir)}"
            ),
        ),
        ids=(
            "local",
            "remote",
        ),
    )
    @pytest.mark.usefixtures("reset_project_context")
    @mock.patch("meltano.cli.params.install_plugins")
    @mock.patch("meltano.cli.add.requests.get")
    def test_add_from_ref(
        self,
        ref_request_mock,
        install_plugin_mock,
        ref,
        project,
        cli_runner,
    ) -> None:
        ref_request_mock.return_value.status_code = 200
        ref_request_mock.return_value.text = plugin_ref.read_text()

        install_plugin_mock.return_value = True

        plugin_name = plugin_ref.parent.name
        plugin_type = PluginType(plugin_ref.parents[1].name)

        res = cli_runner.invoke(
            cli,
            ["add", plugin_type.singular, plugin_name, "--from-ref", ref],
        )
        assert_cli_runner(res)

        assert f"Added {plugin_type.singular} '{plugin_name}'" in res.output

        plugin = project.plugins.find_plugin(plugin_name, plugin_type)
        assert plugin.name == plugin_name
        assert plugin.variant == "test"

    @pytest.mark.usefixtures("reset_project_context")
    @pytest.mark.parametrize(
        (
            "ref",
            "invalid_reason",
        ),
        (
            (
                plugin_ref.name,
                "No such file or directory: '{ref}'",
            ),
            pytest.param(
                plugin_ref.parent,
                "Is a directory: '{ref}'",
                marks=fails_on_windows,
            ),
            (
                "https://:",
                "Invalid URL '{ref}'",
            ),
        ),
        ids=(
            "does not exist",
            "is directory",
            "invalid url",
        ),
    )
    def test_add_from_ref_invalid_ref(
        self,
        ref,
        invalid_reason,
        cli_runner,
    ) -> None:
        res = cli_runner.invoke(
            cli,
            ["add", "extractor", "tap-custom", "--from-ref", ref],
        )

        assert res.exit_code == 2
        assert invalid_reason.format(ref=ref) in res.stderr

    @pytest.mark.parametrize(
        (
            "definition",
            "invalid_reason",
        ),
        (
            (
                "test",
                "incorrect format",
            ),
            (
                {},
                "missing properties (name, namespace)",
            ),
            (
                {"test-key": "test-value"},
                "missing properties (name, namespace)",
            ),
            (
                {"name": "tap-custom"},
                "missing properties (namespace)",
            ),
        ),
        ids=(
            "incorrect format",
            "empty",
            "no required properties",
            "some required properties",
        ),
    )
    def test_add_from_ref_invalid_definiton(
        self,
        definition,
        invalid_reason,
        cli_runner,
    ) -> None:
        with open("test.yml", "w") as f:  # noqa: PTH123
            yaml.dump(definition, f)

        res = cli_runner.invoke(
            cli,
            ["add", "extractor", "tap-custom", "--from-ref", f.name],
        )

        assert res.exit_code == 1
        assert isinstance(res.exception, InvalidPluginDefinitionError)
        assert res.exception.reason == invalid_reason

    def test_add_with_python_version(self, cli_runner: CliRunner) -> None:
        with mock.patch(
            "meltano.core.venv_service._resolve_python_path",
        ) as venv_mock, mock.patch("meltano.core.venv_service.VenvService.install"):
            python = "python3.X"
            assert_cli_runner(
                cli_runner.invoke(
                    cli,
                    (
                        "add",
                        "extractor",
                        "tap-that-needs-custom-python",
                        "--python",
                        python,
                    ),
                ),
            )
            venv_mock.assert_called_with(python)

    def test_add_with_force_flag(self, project: Project, cli_runner: CliRunner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli,
                ["add", "extractor", "tap-gitlab", "--force-install"],
            )
            tap_gitlab = project.plugins.find_plugin(
                "tap-gitlab",
                PluginType.EXTRACTORS,
            )

        assert_cli_runner(res)
        assert tap_gitlab
        install_plugin_mock.assert_called_once_with(
            project,
            [tap_gitlab],
            reason=PluginInstallReason.ADD,
            force=True,
        )

    @pytest.mark.usefixtures("reset_project_context")
    def test_add_update(self, cli_runner) -> None:
        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])
            assert res.exit_code == 0, res.stdout
            assert "Added extractor 'tap-mock" in res.stdout

            res = cli_runner.invoke(
                cli,
                ["add", "extractor", "tap-mock", "--update"],
            )
            assert res.exit_code == 0, res.stdout
            assert "Updated extractor 'tap-mock" in res.stdout

    @pytest.mark.usefixtures("reset_project_context")
    def test_add_update_not_in_project(self, cli_runner) -> None:
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock", "--update"])

        assert res.exit_code == 1
        assert res.exception
        assert str(res.exception) == "Extractor 'tap-mock' is not known to Meltano"

    def test_lockfile_exists(self, cli_runner) -> None:
        plugins_dir = Path("plugins/utilities")
        plugins_dir.mkdir(parents=True, exist_ok=True)
        lockfile = plugins_dir / "utility-mock--original.lock"
        lockfile.write_text(
            json.dumps(
                {
                    "plugin_type": "utilities",
                    "name": "utility-mock",
                    "namespace": "utility_mock",
                },
            ),
        )
        lockfile.touch()

        with mock.patch("meltano.cli.params.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", "utility", "utility-mock"])
            assert res.exit_code == 0, res.stdout
            assert "Plugin definition is already locked at" in res.stdout
            assert "You can remove the file manually" in res.stdout
