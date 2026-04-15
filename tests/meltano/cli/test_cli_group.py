from __future__ import annotations

import pytest
from click.testing import CliRunner

from meltano.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_run_command_has_grouped_options(runner):
    """Ensure grouped headings appear in `meltano run --help`."""
    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0, result.output

    output = result.output

    assert "Run options:" in output
    assert "State options:" in output
    assert "Installation options:" in output
    assert "Global options:" in output


def test_options_present_in_correct_groups(runner):
    """Ensure key options appear under expected groups."""
    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0, result.output
    output = result.output

    # Locate sections
    run_idx = output.find("Run options:")
    state_idx = output.find("State options:")
    install_idx = output.find("Installation options:")
    global_idx = output.find("Global options:")

    run_section = output[run_idx:state_idx]
    state_section = output[state_idx:install_idx]
    install_section = output[install_idx:global_idx]
    global_section = output[global_idx:]

    # Run options
    assert "--dry-run" in run_section
    assert "--full-refresh" in run_section

    # State options
    assert "--no-state-update" in state_section
    assert "--state-id-suffix" in state_section

    # Installation options
    assert "--install" in install_section

    # Global options (sanity check: something that falls in else block)
    assert "--help" in global_section


def test_group_order_is_correct(runner):
    """Ensure groups appear in the intended order."""
    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0, result.output
    output = result.output

    run_idx = output.find("Run options:")
    state_idx = output.find("State options:")
    install_idx = output.find("Installation options:")
    global_idx = output.find("Global options:")

    assert run_idx != -1
    assert state_idx != -1
    assert install_idx != -1
    assert global_idx != -1

    assert run_idx < state_idx < install_idx < global_idx


def test_no_empty_groups_printed(runner):
    """Ensure no unexpected/empty groups are printed."""
    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0, result.output
    output = result.output

    # These are the only expected groups
    expected_groups = {
        "Run options:",
        "State options:",
        "Installation options:",
        "Global options:",
    }

    # Extract all lines ending with "options:"
    found_groups = {
        line.strip()
        for line in output.splitlines()
        if line.strip().endswith("options:")
    }

    # Ensure no extra groups exist
    assert found_groups.issubset(expected_groups)
