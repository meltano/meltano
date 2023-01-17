from __future__ import annotations

import random

import pytest

from meltano.core.tracking.contexts.environment import EnvironmentContext


def test_environment_context(monkeypatch: pytest.MonkeyPatch):
    for notable_flag_env_var in EnvironmentContext.notable_flag_env_vars:
        monkeypatch.delenv(notable_flag_env_var, raising=False)

    assert EnvironmentContext().data["notable_flag_env_vars"] == {}  # noqa: WPS520

    truthy_values = ("Yes", "TRUE", "1", "true", "y", "on", "t")
    truthy_flags = {}
    for notable_flag_env_var in EnvironmentContext.notable_flag_env_vars:
        truthy_flags[notable_flag_env_var] = random.choice(truthy_values)  # noqa: S311
        monkeypatch.setenv(notable_flag_env_var, truthy_flags[notable_flag_env_var])

    assert EnvironmentContext().data["notable_flag_env_vars"] == truthy_flags
