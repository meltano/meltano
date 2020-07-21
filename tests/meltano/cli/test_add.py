import os
import pytest
import functools
import yaml
from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.plugin import PluginType, PluginRef
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin.error import PluginMissingError
from meltano.core.m5o.dashboards_service import DashboardsService
from meltano.core.m5o.reports_service import ReportsService


class TestCliAdd:
    @pytest.mark.parametrize(
        "plugin_type,plugin_name,related_plugins",
        [
            (PluginType.EXTRACTORS, "tap-carbon-intensity", []),
            (PluginType.LOADERS, "target-sqlite", []),
            (
                PluginType.TRANSFORMS,
                "tap-carbon-intensity",
                [
                    PluginRef(PluginType.TRANSFORMERS, "dbt"),
                    PluginRef(PluginType.FILES, "dbt"),
                ],
            ),
            (PluginType.MODELS, "model-carbon-intensity", []),
            (PluginType.DASHBOARDS, "dashboard-google-analytics", []),
            (
                PluginType.ORCHESTRATORS,
                "airflow",
                [PluginRef(PluginType.FILES, "airflow")],
            ),
            # Installed automatically because of transform 'tap-carbon-intensity'
            # (PluginType.TRANSFORMERS, "dbt", [PluginRef(PluginType.FILES, "dbt")]),
        ],
    )
    def test_add(
        self,
        plugin_type,
        plugin_name,
        related_plugins,
        project,
        cli_runner,
        config_service,
    ):
        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin(plugin_name, plugin_type=plugin_type)

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(cli, ["add", plugin_type.singular, plugin_name])

            assert res.exit_code == 0, res.stdout
            assert f"Added {plugin_type.descriptor} '{plugin_name}'" in res.stdout

            plugin = config_service.find_plugin(plugin_name, plugin_type)
            assert plugin
            plugins = [plugin]

            for related_plugin in related_plugins:
                plugin_install = config_service.find_plugin(
                    related_plugin.name, related_plugin.type
                )
                assert plugin_install

                assert (
                    f"Added related {related_plugin.type.descriptor} '{related_plugin.name}'"
                    in res.stdout
                )

                plugins.append(plugin_install)

            plugins.reverse()

            install_plugin_mock.assert_called_once_with(
                project, plugins, reason=PluginInstallReason.ADD
            )

    def test_add_multiple(self, project, cli_runner, config_service):
        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            cli_runner.invoke(cli, ["add", "extractors", "tap-gitlab"])

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            res = cli_runner.invoke(
                cli, ["add", "extractors", "tap-gitlab", "tap-adwords", "tap-facebook"]
            )

            assert res.exit_code == 0, res.stdout
            assert (
                f"Extractor 'tap-gitlab' is already in your Meltano project"
                in res.stderr
            )
            assert f"Added extractor 'tap-adwords'" in res.stdout
            assert f"Added extractor 'tap-facebook'" in res.stdout

            tap_gitlab = config_service.find_plugin("tap-gitlab", PluginType.EXTRACTORS)
            assert tap_gitlab
            tap_adwords = config_service.find_plugin(
                "tap-adwords", PluginType.EXTRACTORS
            )
            assert tap_adwords
            tap_facebook = config_service.find_plugin(
                "tap-facebook", PluginType.EXTRACTORS
            )
            assert tap_facebook

            install_plugin_mock.assert_called_once_with(
                project,
                [tap_facebook, tap_adwords, tap_gitlab],
                reason=PluginInstallReason.ADD,
            )

    def test_add_transform(self, project, cli_runner):
        cli_runner.invoke(cli, ["add", "files", "dbt"])
        cli_runner.invoke(cli, ["install", "files", "dbt"])

        res = cli_runner.invoke(cli, ["add", "transform", "tap-google-analytics"])
        assert_cli_runner(res)

        with project.root_dir("transform/packages.yml").open() as packages_file:
            packages_yaml = yaml.safe_load(packages_file)

        with project.root_dir("transform/dbt_project.yml").open() as project_file:
            project_yaml = yaml.safe_load(project_file)

        assert {
            "git": "https://gitlab.com/meltano/dbt-tap-google-analytics.git"
        } in packages_yaml["packages"]

        assert "tap_google_analytics" in project_yaml["models"]
        assert project_yaml["models"]["tap_google_analytics"] == {
            "vars": {"schema": "{{ env_var('DBT_SOURCE_SCHEMA') }}"}
        }

    def test_add_dashboard(self, project, cli_runner):
        def install():
            return cli_runner.invoke(
                cli, ["add", "dashboard", "dashboard-google-analytics"]
            )

        res = install()
        assert res.exit_code == 0

        dashboards_service = DashboardsService(project)
        dashboards_count = len(dashboards_service.get_dashboards())

        assert dashboards_count > 0

        reports_service = ReportsService(project)
        reports_count = len(reports_service.get_reports())
        assert reports_count > 0

        # Verify that reinstalling doesn't duplicate dashboards and reports
        res = install()
        assert res.exit_code == 0

        assert len(dashboards_service.get_dashboards()) == dashboards_count
        assert len(reports_service.get_reports()) == reports_count

    def test_add_files_with_updates(
        self,
        session,
        project,
        cli_runner,
        config_service,
        plugin_settings_service_factory,
    ):
        result = cli_runner.invoke(cli, ["add", "files", "airflow"])
        assert_cli_runner(result)

        # Plugin has been added to meltano.yml
        plugin = config_service.find_plugin("airflow", PluginType.FILES)
        assert plugin

        # Automatic updating is enabled
        plugin_settings_service = plugin_settings_service_factory(plugin)
        value = plugin_settings_service.get(
            "update.orchestrate/dags/meltano.py", session=session
        )
        assert value == True

        # File has been created
        assert "Created orchestrate/dags/meltano.py" in result.output

        file_path = project.root_dir("orchestrate/dags/meltano.py")
        assert file_path.is_file()

        # File has "managed" header
        assert (
            "This file is managed by the 'airflow' file bundle" in file_path.read_text()
        )

    def test_add_files_without_updates(self, project, cli_runner, config_service):
        result = cli_runner.invoke(cli, ["add", "files", "docker-compose"])
        assert_cli_runner(result)

        # Plugin has not been added to meltano.yml
        with pytest.raises(PluginMissingError):
            config_service.find_plugin("docker-compose", PluginType.FILES)

        # File has been created
        assert "Created docker-compose.yml" in result.output

        file_path = project.root_dir("docker-compose.yml")
        assert file_path.is_file()

        # File does not have "managed" header
        assert "This file is managed" not in file_path.read_text()

    def test_add_files_that_already_exists(self, project, cli_runner, config_service):
        project.root_dir("transform/dbt_project.yml").write_text("Exists!")

        result = cli_runner.invoke(cli, ["add", "files", "dbt"])
        assert_cli_runner(result)

        assert (
            "File transform/dbt_project.yml already exists, keeping both versions"
            in result.output
        )
        assert "Created transform/dbt_project (dbt).yml" in result.output
        assert project.root_dir("transform/dbt_project (dbt).yml").is_file()

    def test_add_related(self, project, cli_runner, config_service):
        # Add dbt and transform/ files
        cli_runner.invoke(cli, ["add", "transformer", "dbt"])
        cli_runner.invoke(cli, ["add", "files", "dbt"])

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli, ["add", "--include-related", "extractor", "tap-gitlab"]
            )
            assert res.exit_code == 0

            tap = config_service.find_plugin("tap-gitlab", PluginType.EXTRACTORS)
            assert tap
            transform = config_service.find_plugin("tap-gitlab", PluginType.TRANSFORMS)
            assert transform
            model = config_service.find_plugin("model-gitlab", PluginType.MODELS)
            assert model
            dashboard = config_service.find_plugin(
                "dashboard-gitlab", PluginType.DASHBOARDS
            )
            assert dashboard

            install_plugin_mock.assert_called_once_with(
                project,
                [dashboard, model, transform, tap],
                reason=PluginInstallReason.ADD,
            )

    def test_add_missing(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-unknown"])

        assert res.exit_code == 1
        assert "extractor 'tap-unknown' is not known to Meltano" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin("tap-unknown", PluginType.EXTRACTORS)

    @pytest.mark.xfail(reason="Uninstall not implemented yet.")
    def test_add_fails(self, project, cli_runner, config_service):
        res = cli_runner.invoke(cli, ["add", "extractor", "tap-mock"])

        assert res.exit_code == 1, res.stdout
        assert "Failed to install plugin 'tap-mock'" in res.stdout
        assert res.stderr

        # ensure the plugin is not present
        with pytest.raises(PluginMissingError):
            config_service.find_plugin("tap-mock", PluginType.EXTRACTORS)

    def test_add_custom(self, project, cli_runner, config_service):
        stdin = os.linesep.join(
            # namespace, executable, pip_url
            ["custom", "-e path/to/tap-custom", "tap-custom-bin"]
        )

        with mock.patch("meltano.cli.add.install_plugins") as install_plugin_mock:
            install_plugin_mock.return_value = True
            res = cli_runner.invoke(
                cli, ["add", "--custom", "extractor", "tap-custom"], input=stdin
            )

            plugin = config_service.find_plugin("tap-custom", PluginType.EXTRACTORS)
            assert plugin.name == "tap-custom"
            assert plugin.executable == "tap-custom-bin"

            install_plugin_mock.assert_called_once_with(
                project, [plugin], reason=PluginInstallReason.ADD
            )
