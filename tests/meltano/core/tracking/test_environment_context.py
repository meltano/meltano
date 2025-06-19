from __future__ import annotations

import random
import typing as t

from meltano.core.tracking.contexts.environment import EnvironmentContext
from meltano.core.utils import hash_sha256

if t.TYPE_CHECKING:
    import pytest


def test_notable_flag_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    for notable_flag_env_var in EnvironmentContext.notable_flag_env_vars:
        monkeypatch.delenv(notable_flag_env_var, raising=False)

    assert EnvironmentContext().data["notable_flag_env_vars"] == {}

    def check(env_var_values: tuple[str, ...], *, expected: bool | None) -> None:
        for notable_flag_env_var in EnvironmentContext.notable_flag_env_vars:
            monkeypatch.setenv(
                notable_flag_env_var,
                random.choice(env_var_values),  # noqa: S311
            )

        assert EnvironmentContext().data["notable_flag_env_vars"] == dict.fromkeys(
            EnvironmentContext.notable_flag_env_vars,
            expected,
        )

    check(("Yes", "TRUE", "1", "true", "y", "on", "t"), expected=True)
    check(("No", "FALSE", "0", "false", "n", "off", "f"), expected=False)
    check(("trew", "Fallse", "nah", "si", "okay", "01"), expected=None)


def test_notable_hashed_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    for notable_hashed_env_var in EnvironmentContext.notable_hashed_env_vars:
        monkeypatch.delenv(notable_hashed_env_var, raising=False)
    assert EnvironmentContext().data["notable_hashed_env_vars"] == {}

    github_username = "test_user"
    monkeypatch.setenv("GITHUB_USER", github_username)
    assert EnvironmentContext().data["notable_hashed_env_vars"] == {
        "GITHUB_USER": hash_sha256(github_username),
    }

    github_repo = "test_owner/test_repo"
    monkeypatch.setenv("GITHUB_REPOSITORY", github_repo)
    assert EnvironmentContext().data["notable_hashed_env_vars"] == {
        "GITHUB_USER": hash_sha256(github_username),
        "GITHUB_REPOSITORY": hash_sha256(github_repo),
    }
