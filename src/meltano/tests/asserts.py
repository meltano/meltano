from __future__ import annotations

from click.testing import Result


def assert_cli_runner(results: Result, message=None):
    assertion_message = str(message or results.output)

    assert results.exit_code == 0, assertion_message
