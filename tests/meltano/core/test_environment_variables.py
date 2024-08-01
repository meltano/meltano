from __future__ import annotations

import platform
import subprocess
import typing as t

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.settings_service import FEATURE_FLAG_PREFIX, FeatureFlags
from meltano.core.utils import EnvironmentVariableNotSetError


class EnvVarResolutionExpectation(t.NamedTuple):
    expected_env_values: dict
    meltanofile_updates: t.ClassVar[dict] = {}
    terminal_env: t.ClassVar[dict] = {}


def _meltanofile_update_dict(
    *,
    top_level_plugin_setting=True,
    top_level_plugin_config=False,
    top_level_env=False,
    top_level_plugin_env=False,
    environment_level_env=False,
    environment_level_plugin_env=False,
    environment_level_plugin_config=False,
    environment_level_plugin_config_indirected=False,
):
    plugin_name = "test-env-var-resolution"
    plugin_namespace = plugin_name.replace("-", "_")
    setting = {
        "name": "from",
        "kind": "string",
    }
    env = {}
    environment = {"name": "dev"}
    utility = {
        "name": plugin_name,
        "namespace": plugin_namespace,
        "settings": [setting],
        "executable": "pwd",
    }
    if top_level_plugin_setting:
        setting["value"] = "top_level_plugin_setting"
    if top_level_plugin_config:
        utility["config"] = {"from": "top_level_plugin_config"}
    if top_level_env:
        env["TEST_ENV_VAR_RESOLUTION_FROM"] = "top_level_env"
    if top_level_plugin_env:
        utility["env"] = {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_env"}
    if environment_level_plugin_config:
        environment["config"] = {
            "plugins": {
                "utilities": [
                    {
                        "name": plugin_name,
                        "config": {"from": "environment_level_plugin_config"},
                    },
                ],
            },
        }
    if environment_level_env:
        environment["env"] = {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"}
    if environment_level_plugin_env:
        environment["config"] = {
            "plugins": {
                "utilities": [
                    {
                        "name": plugin_name,
                        "env": {
                            "TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_env",  # noqa: E501
                        },
                    },
                ],
            },
        }
    if environment_level_plugin_config_indirected:
        environment.update(
            {
                "config": {
                    "plugins": {
                        "utilities": [
                            {
                                "name": plugin_name,
                                "config": {"from": "$INDIRECTED_ENV_VAR"},
                            },
                        ],
                    },
                },
                "env": {
                    "INDIRECTED_ENV_VAR": "environment_level_plugin_config_indirected",
                },
            },
        )
    return {
        "plugins": {"utilities": [utility]},
        "environments": [environment],
        "env": env,
    }


_terminal_env_var = {"TEST_ENV_VAR_RESOLUTION_FROM": "terminal_env"}

_env_var_resolution_expectations = {
    # Check that envs at each level override terminal
    "00 Terminal environment": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "terminal_env"},
        _meltanofile_update_dict(),
        _terminal_env_var,
    ),
    "01 Top-level env (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_env"},
        _meltanofile_update_dict(top_level_env=True),
        _terminal_env_var,
    ),
    "02 Top-level plugin env (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_env"},
        _meltanofile_update_dict(top_level_plugin_env=True),
        _terminal_env_var,
    ),
    "03 Environment-level env (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(environment_level_env=True),
        _terminal_env_var,
    ),
    "04 Environment-level plugin env (with terminal context)": EnvVarResolutionExpectation(  # noqa: E501
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_env"},
        _meltanofile_update_dict(environment_level_plugin_env=True),
        _terminal_env_var,
    ),
    # Now check the order of precedence between each level
    "06 Top-level env": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_env"},
        _meltanofile_update_dict(top_level_env=True),
    ),
    "07 Top-level plugin env (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_env"},
        _meltanofile_update_dict(top_level_env=True, top_level_plugin_env=True),
    ),
    "08 Environment-level env": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            top_level_env=True,
            top_level_plugin_env=True,
            environment_level_env=True,
        ),
    ),
    "09 Environment-level Plugin env": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_env"},
        _meltanofile_update_dict(
            top_level_env=True,
            top_level_plugin_env=True,
            environment_level_env=True,
            environment_level_plugin_env=True,
        ),
    ),
    "10 Top-level plugin setting (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "terminal_env"},
        _meltanofile_update_dict(top_level_plugin_setting=True),
        _terminal_env_var,
    ),
    "11 Top-level plugin config (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
        ),
        _terminal_env_var,
    ),
    "12 Environment-level plugin config (with terminal context)": EnvVarResolutionExpectation(  # noqa: E501
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
        ),
        _terminal_env_var,
    ),
    "13 Top-level plugin setting": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
        ),
    ),
    "14 Set in top-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
        ),
    ),
    "15 Environment-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
        ),
    ),
    "16 Set in indirected environment-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_config_indirected"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
            environment_level_plugin_config_indirected=True,
        ),
    ),
}


class TestEnvVarResolution:
    @pytest.mark.parametrize(
        ("expected_env_values", "meltanofile_updates", "terminal_env"),
        [tuple(x) for x in _env_var_resolution_expectations.values()],
        ids=_env_var_resolution_expectations.keys(),
    )
    @pytest.mark.usefixtures("cli_runner")
    def test_env_var_resolution(
        self,
        expected_env_values,
        meltanofile_updates,
        terminal_env,
        project,
        monkeypatch,
    ) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/3444",
            )

        for key, val in terminal_env.items():
            monkeypatch.setenv(key, val)

        with project.meltano_update() as meltanofile:
            meltanofile.update(meltanofile_updates)

        result = subprocess.run(
            (
                "meltano",
                "invoke",
                *(arg for key in expected_env_values for arg in ("--print-var", key)),
                "test-env-var-resolution",
            ),
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        assert result.stdout.strip().split("\n")[:-1] == [
            f"{env_key}={env_val}" for env_key, env_val in expected_env_values.items()
        ]


def test_environment_variable_inheritance(cli_runner, project, monkeypatch) -> None:
    monkeypatch.setenv("STACKED", "1")
    with project.meltano_update() as meltanofile:
        meltanofile.update(
            {
                "env": {"STACKED": "${STACKED}2"},
                "plugins": {
                    "utilities": [
                        {
                            "name": "test-environment-inheritance",
                            "namespace": "test_environment_inheritance",
                            "executable": "pwd",
                            "env": {"STACKED": "${STACKED}4"},
                        },
                    ],
                },
                "environments": [
                    {
                        "name": "dev",
                        "env": {"STACKED": "${STACKED}3"},
                        "config": {
                            "plugins": {
                                "utilities": [
                                    {
                                        "name": "test-environment-inheritance",
                                        "env": {"STACKED": "${STACKED}5"},
                                    },
                                ],
                            },
                        },
                    },
                ],
            },
        )
    result = cli_runner.invoke(
        cli,
        [
            "invoke",
            "--print-var",
            "STACKED",
            "test-environment-inheritance",
        ],
    )
    assert_cli_runner(result)
    assert result.stdout.strip() == "STACKED=12345"


def test_environment_variable_inheritance_meltano_env_only(
    cli_runner,
    project,
    monkeypatch,
) -> None:
    monkeypatch.setenv("STACKED", "1")
    with project.meltano_update() as meltanofile:
        meltanofile.update(
            {
                "plugins": {
                    "utilities": [
                        {
                            "name": "test-environment-inheritance",
                            "namespace": "test_environment_inheritance",
                            "executable": "pwd",
                        },
                    ],
                },
                "environments": [
                    {
                        "name": "dev",
                        "env": {"STACKED": "${STACKED}2"},
                    },
                ],
            },
        )
    result = cli_runner.invoke(
        cli,
        [
            "invoke",
            "--print-var",
            "STACKED",
            "test-environment-inheritance",
        ],
    )
    assert_cli_runner(result)
    assert result.stdout.strip() == "STACKED=12"


def test_strict_env_var_mode_raises_full_replace(cli_runner, project) -> None:
    project.settings.set(
        [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
        value=True,
    )
    with project.meltano_update() as meltanofile:
        meltanofile.update(_meltanofile_update_dict())
        meltanofile.update({"env": {"some_var": "$NONEXISTENT"}})
    result = cli_runner.invoke(
        cli,
        [
            "invoke",
            "--print-var",
            "STACKED",
            "test-env-var-resolution",
        ],
    )
    assert isinstance(result.exception, EnvironmentVariableNotSetError)
    assert (
        result.exception.reason
        == "Environment variable 'NONEXISTENT' referenced but not set"
    )
    assert result.exception.instruction == "Make sure the environment variable is set"


def test_strict_env_var_mode_raises_partial_replace(cli_runner, project) -> None:
    project.settings.set(
        [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)],
        value=True,
    )
    with project.meltano_update() as meltanofile:
        meltanofile.update(_meltanofile_update_dict())
        meltanofile.update({"env": {"some_var": "some_${NONEXISTENT}_value"}})
    result = cli_runner.invoke(
        cli,
        [
            "invoke",
            "--print-var",
            "STACKED",
            "test-env-var-resolution",
        ],
    )
    exception = result.exception
    assert isinstance(exception, EnvironmentVariableNotSetError)
    assert (
        result.exception.reason
        == "Environment variable 'NONEXISTENT' referenced but not set"
    )
    assert result.exception.instruction == "Make sure the environment variable is set"
