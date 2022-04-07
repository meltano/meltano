from unittest import mock

from asserts import assert_cli_runner
from meltano.cli import cli


class TestCliUpgrade:
    def test_upgrade(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade"])
        assert_cli_runner(result)

        assert (
            "The `meltano` package could not be upgraded automatically" in result.output
        )
        assert "run `meltano upgrade --skip-package`" in result.output

        with mock.patch(
            "meltano.cli.upgrade.UpgradeService._upgrade_package"
        ) as upgrade_package_mock:
            upgrade_package_mock.return_value = True

            result = cli_runner.invoke(cli, ["upgrade"])
            assert_cli_runner(result)

            assert (
                "Meltano and your Meltano project have been upgraded!" in result.output
            )

    def test_upgrade_skip_package(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "--skip-package"])
        assert_cli_runner(result)

        assert "Your Meltano project has been upgraded!" in result.output

    def test_upgrade_package(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "package"])
        assert_cli_runner(result)

        assert (
            "The `meltano` package could not be upgraded automatically" in result.output
        )
        assert "run `meltano upgrade --skip-package`" not in result.output

    def test_upgrade_files(self, session, project, cli_runner, config_service):
        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Nothing to update" in result.output

        result = cli_runner.invoke(cli, ["add", "files", "airflow"])
        assert_cli_runner(result)

        # Don't update file if unchanged
        file_path = project.root_dir("orchestrate/dags/meltano.py")
        file_content = file_path.read_text()

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updating 'airflow' files in project..." in result.output
        assert "Nothing to update" in result.output
        assert file_path.read_text() == file_content

        # Update file if changed
        file_path.write_text("Overwritten!")

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updated orchestrate/dags/meltano.py" in result.output
        assert file_path.read_text() == file_content

        # Don't update file if unchanged
        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Nothing to update" in result.output
        assert file_path.read_text() == file_content

        # Don't update file if automatic updating is disabled
        result = cli_runner.invoke(
            cli,
            [
                "config",
                "--plugin-type",
                "files",
                "airflow",
                "set",
                "_update",
                "orchestrate/dags/meltano.py",
                "false",
            ],
        )
        assert_cli_runner(result)

        file_path.write_text("Overwritten!")

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Nothing to update" in result.output
        assert file_path.read_text() != file_content

        # Update file if automatic updating is re-enabled
        result = cli_runner.invoke(
            cli,
            [
                "config",
                "--plugin-type",
                "files",
                "airflow",
                "unset",
                "_update",
                "orchestrate/dags/meltano.py",
            ],
        )
        assert_cli_runner(result)

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updated orchestrate/dags/meltano.py" in result.output

    def test_upgrade_database(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "database"])
        assert_cli_runner(result)

    def test_upgrade_models(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "models"])
        assert_cli_runner(result)
