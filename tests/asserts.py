from __future__ import annotations

import traceback
import typing as t

if t.TYPE_CHECKING:
    from click.testing import Result


def assert_cli_runner(results: Result, message=None) -> None:
    assertion_message = str(message or results.output)

    if results.exception:
        assertion_message += "".join(
            ("\n", *traceback.format_exception(*results.exc_info)),
        )

    assert results.exit_code == 0, assertion_message
