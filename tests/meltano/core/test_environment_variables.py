from __future__ import annotations

import platform
from typing import NamedTuple

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import FEATURE_FLAG_PREFIX, FeatureFlags
from meltano.core.utils import EnvironmentVariableNotSetError


class EnvVarResolutionExpectation(NamedTuple):
    expected_env_values: dict
    meltanofile_updates: dict = {}
    terminal_env: dict = {}


def _meltanofile_update_dict(
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
        setting.update({"value": "top_level_plugin_setting"})
    if top_level_plugin_config:
        utility.update({"config": {"from": "top_level_plugin_config"}})
    if top_level_env:
        env.update({"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_env"})
    if top_level_plugin_env:
        utility.update(
            {"env": {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_env"}}
        )
    if environment_level_plugin_config:
        environment.update(
            {
                "config": {
                    "plugins": {
                        "utilities": [
                            {
                                "name": plugin_name,
                                "config": {"from": "environment_level_plugin_config"},
                            }
                        ]
                    }
                }
            }
        )
    if environment_level_env:
        environment.update(
            {"env": {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_env"}}
        )
    if environment_level_plugin_env:
        environment.update(
            {
                "config": {
                    "plugins": {
                        "utilities": [
                            {
                                "name": plugin_name,
                                "env": {
                                    "TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_env"
                                },
                            }
                        ]
                    }
                }
            }
        )
    if environment_level_plugin_config_indirected:
        environment.update(
            {
                "config": {
                    "plugins": {
                        "utilities": [
                            {
                                "name": plugin_name,
                                "config": {"from": "$INDIRECTED_ENV_VAR"},
                            }
                        ]
                    }
                },
                "env": {
                    "INDIRECTED_ENV_VAR": "environment_level_plugin_config_indirected"
                },
            }
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
    "04 Environment-level plugin env (with terminal context)": EnvVarResolutionExpectation(
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
            top_level_env=True, top_level_plugin_env=True, environment_level_env=True
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
    "12 Environment-level plugin config (with terminal context)": EnvVarResolutionExpectation(
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
            environment_level_env=True, top_level_plugin_setting=True
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
        "scenario,env_var_resolution_expectation,",
        _env_var_resolution_expectations.items(),
    )
    def test_env_var_resolution(
        self, scenario, env_var_resolution_expectation, cli_runner, project, monkeypatch
    ):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        with project.meltano_update() as meltanofile:
            meltanofile.update(env_var_resolution_expectation.meltanofile_updates)

        for key, val in env_var_resolution_expectation.terminal_env.items():
            monkeypatch.setenv(key, val)

        args = ["invoke"]
        for key in env_var_resolution_expectation.expected_env_values.keys():
            args.extend(("--print-var", key))
        args.append("test-env-var-resolution")
        result = cli_runner.invoke(cli, args)
        assert_cli_runner(result)
        assert result.stdout.strip() == "\n".join(
            [
                f"{env_key}={env_val}"
                for env_key, env_val in env_var_resolution_expectation.expected_env_values.items()
            ]
        )


def test_environment_variable_inheritance(cli_runner, project, monkeypatch):
    # This test will be resolved to pass as part of
    # this issue: https://github.com/meltano/meltano/issues/5983
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
                        }
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
                                    }
                                ]
                            }
                        },
                    }
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
    cli_runner, project, monkeypatch
):
    # This test will be resolved to pass as part of
    # this issue: https://github.com/meltano/meltano/issues/5983
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
                        }
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


def test_strict_env_var_mode_raises_full_replace(cli_runner, project):
    project_settings_service = ProjectSettingsService(project)
    project_settings_service.set(
        [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)], True
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


def test_strict_env_var_mode_raises_partial_replace(cli_runner, project):
    project_settings_service = ProjectSettingsService(project)
    project_settings_service.set(
        [FEATURE_FLAG_PREFIX, str(FeatureFlags.STRICT_ENV_VAR_MODE)], True
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
