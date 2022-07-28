import platform
from typing import NamedTuple

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli


class EnvVarResolutionExpectation(NamedTuple):
    expected_env_values: dict
    meltanofile_updates: dict = {}
    terminal_env: dict = {}
    xfail: bool = False


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
                    "INDIRECTED_ENV_VAR": "environment_level_plugin_config_indrected"
                },
            }
        )
    return {
        "plugins": {"utilities": [utility]},
        "environments": [environment],
        "env": env,
    }


_terminal_env_var = {"TEST_ENV_VAR_RESOLUTION_FROM": "terminal_env"}

# Test cases with xfail=True should be resolved to pass
# as part of this issue: https://github.com/meltano/meltano/issues/5982
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
    # Original xfail'ing tests, as per comment above
    "10 Top-level plugin setting (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_setting"},
        _meltanofile_update_dict(top_level_plugin_setting=True),
        _terminal_env_var,
        xfail=True,
    ),
    "11 Top-level plugin config (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_config"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
        ),
        _terminal_env_var,
        xfail=True,
    ),
    "12 Environment-level plugin config (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_config"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
        ),
        _terminal_env_var,
        xfail=True,
    ),
    "13 Set in indirected environment-level plugin config (with terminal context)": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_config_indrected"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
            environment_level_plugin_config_indirected=True,
        ),
        _terminal_env_var,
        xfail=True,
    ),
    "14 Top-level plugin setting": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_setting"},
        _meltanofile_update_dict(
            environment_level_env=True, top_level_plugin_setting=True
        ),
        xfail=True,
    ),
    "15 Set in top-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "top_level_plugin_config"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
        ),
        xfail=True,
    ),
    "16 Environment-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_config"},
        _meltanofile_update_dict(
            environment_level_env=True,
            top_level_plugin_setting=True,
            top_level_plugin_config=True,
            environment_level_plugin_config=True,
        ),
        xfail=True,
    ),
    "17 Set in indirected environment-level plugin config": EnvVarResolutionExpectation(
        {"TEST_ENV_VAR_RESOLUTION_FROM": "environment_level_plugin_config_indrected"},
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

        if env_var_resolution_expectation.xfail:
            pytest.xfail(
                "This expected environment variable resolution behavior is currently failing."
            )
        args = ["invoke"]
        for key in env_var_resolution_expectation.expected_env_values.keys():
            args.append("--print-var")
            args.append(key)
        args.append("test-env-var-resolution")
        result = cli_runner.invoke(cli, args)
        assert_cli_runner(result)
        assert result.stdout.strip() == "\n".join(
            [
                f"{env_key}={env_val}"
                for env_key, env_val in env_var_resolution_expectation.expected_env_values.items()
            ]
        )

    @pytest.mark.xfail
    def test_environment_variable_inheritance(self, cli_runner, project, monkeypatch):
        # This test will be resolved to pass as part of
        # this issue: https://github.com/meltano/meltano/issues/5983
        monkeypatch.setenv("STACKED", "1")
        with project.meltano_update() as meltanofile:
            meltanofile.update(
                {
                    "env": "${STACKED}2",
                    "plugins": {
                        "utilities": [
                            {
                                "name": "test-environment-inheritance",
                                "namespace": "test_environment_inheritance",
                                "executable": "pwd",
                                "env": "${STACKED}4",
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

    @pytest.mark.xfail
    def test_environment_variable_inheritance_meltano_env_only(
        self, cli_runner, project, monkeypatch
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
