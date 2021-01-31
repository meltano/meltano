from unittest import mock

import pytest
import yaml
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

        result = cli_runner.invoke(cli, ["add", "files", "dbt"])
        assert_cli_runner(result)

        # Don't update file if unchanged
        file_path = project.root_dir("transform/profile/profiles.yml")
        file_content = file_path.read_text()

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updating 'dbt' files in project..." in result.output
        assert "Nothing to update" in result.output
        assert file_path.read_text() == file_content

        # Update file if changed
        file_path.write_text("Overwritten!")

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updated transform/profile/profiles.yml" in result.output
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
                "dbt",
                "set",
                "_update",
                "transform/profile/profiles.yml",
                "false",
            ],
        )
        assert_cli_runner(result)

        file_path.write_text("Overwritten!")

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Nothing to update" in result.output
        assert file_path.read_text() != file_content

        # Update file if automatic updating is enabled
        result = cli_runner.invoke(
            cli,
            [
                "config",
                "--plugin-type",
                "files",
                "dbt",
                "set",
                "_update",
                "transform/dbt_project.yml",
                "true",
            ],
        )
        assert_cli_runner(result)

        result = cli_runner.invoke(cli, ["upgrade", "files"])
        assert_cli_runner(result)

        assert "Updated transform/dbt_project.yml" in result.output

        file_path = project.root_dir("transform/dbt_project.yml")
        assert "This file is managed by the 'dbt' file bundle" in file_path.read_text()

    def test_upgrade_database(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "database"])
        assert_cli_runner(result)

    def test_upgrade_models(self, project, cli_runner):
        result = cli_runner.invoke(cli, ["upgrade", "models"])
        assert_cli_runner(result)
