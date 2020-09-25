import pytest
import os
import shutil
import yaml
import logging
import datetime
from pathlib import Path

import meltano.core.bundle
from meltano.core.project import Project
from meltano.core.behavior.canonical import Canonical
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.config_service import ConfigService, PluginAlreadyAddedException
from meltano.core.schedule_service import ScheduleService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin import PluginRef, PluginType, ProjectPlugin
from meltano.core.plugin.factory import plugin_factory
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.logging.job_logging_service import JobLoggingService


PROJECT_NAME = "a_meltano_project"


@pytest.fixture(scope="class")
def discovery():
    with meltano.core.bundle.find("discovery.yml").open() as base:
        discovery = yaml.safe_load(base)

    discovery[PluginType.EXTRACTORS].append(
        {
            "name": "tap-mock",
            "namespace": "tap_mock",
            "variants": [
                {
                    "name": "meltano",
                    "pip_url": "tap-mock",
                    "capabilities": ["discover", "catalog", "state"],
                    "settings": [
                        {"name": "test", "value": "mock"},
                        {"name": "start_date"},
                        {"name": "protected", "protected": True},
                        {"name": "secure", "kind": "password"},
                        {"name": "port", "kind": "integer", "value": 5000},
                        {"name": "list", "kind": "array", "value": []},
                        {
                            "name": "object",
                            "aliases": ["data"],
                            "kind": "object",
                            "value": {"nested": "from_default"},
                        },
                        {"name": "hidden", "kind": "hidden", "value": 42},
                        {
                            "name": "boolean",
                            "kind": "boolean",
                            "env_aliases": ["TAP_MOCK_ENABLED", "!TAP_MOCK_DISABLED"],
                        },
                    ],
                },
                {
                    "name": "singer-io",
                    "original": True,
                    "deprecated": True,
                    "pip_url": "singer-tap-mock",
                },
            ],
        }
    )

    discovery[PluginType.LOADERS].append(
        {
            "name": "target-mock",
            "namespace": "mock",
            "pip_url": "target-mock",
            "settings": [{"name": "schema", "env": "MOCKED_SCHEMA"}],
        }
    )

    discovery[PluginType.TRANSFORMS].append(
        {
            "name": "tap-mock-transform",
            "namespace": "tap_mock",
            "pip_url": "tap-mock-transform",
            "package_name": "dbt_mock",
        }
    )

    discovery[PluginType.MODELS].append(
        {
            "name": "model-gitlab",
            "namespace": "tap_gitlab",
            "pip_url": "git+https://gitlab.com/meltano/model-gitlab.git",
        }
    )

    discovery[PluginType.DASHBOARDS].append(
        {
            "name": "dashboard-google-analytics",
            "namespace": "tap_google_analytics",
            "pip_url": "git+https://gitlab.com/meltano/dashboard-google-analytics.git",
        }
    )

    discovery[PluginType.ORCHESTRATORS].append(
        {
            "name": "orchestrator-mock",
            "namespace": "pytest",
            "pip_url": "orchestrator-mock",
        }
    )

    discovery[PluginType.TRANSFORMERS].append(
        {
            "name": "transformer-mock",
            "namespace": "transformer_mock",
            "pip_url": "transformer-mock",
        }
    )

    return discovery


@pytest.fixture(scope="class")
def plugin_discovery_service(project, discovery, config_service):
    return PluginDiscoveryService(
        project, discovery=discovery, config_service=config_service
    )


@pytest.fixture(scope="class")
def project_compiler(project):
    return ProjectCompiler(project)


@pytest.fixture(scope="class")
def project_init_service():
    return ProjectInitService(PROJECT_NAME)


@pytest.fixture(scope="class")
def plugin_install_service(project, config_service):
    return PluginInstallService(project, config_service=config_service)


@pytest.fixture(scope="class")
def project_add_service(project, config_service, plugin_discovery_service):
    return ProjectAddService(
        project,
        config_service=config_service,
        plugin_discovery_service=plugin_discovery_service,
    )


@pytest.fixture(scope="class")
def plugin_settings_service_factory(project, config_service, plugin_discovery_service):
    def _factory(plugin, **kwargs):
        return PluginSettingsService(
            project,
            plugin,
            config_service=config_service,
            plugin_discovery_service=plugin_discovery_service,
            **kwargs,
        )

    return _factory


@pytest.fixture(scope="class")
def plugin_invoker_factory(
    project, plugin_settings_service_factory, plugin_discovery_service
):
    def _factory(plugin, **kwargs):
        return invoker_factory(
            project,
            plugin,
            plugin_settings_service=plugin_settings_service_factory(plugin),
            plugin_discovery_service=plugin_discovery_service,
            **kwargs,
        )

    return _factory


@pytest.fixture(scope="class")
def add_model(project, plugin_install_service, project_add_service):
    MODELS = [
        "model-carbon-intensity",
        "model-gitflix",
        "model-salesforce",
        "model-gitlab",
    ]

    for model in MODELS:
        plugin = project_add_service.add(PluginType.MODELS, model)
        plugin_install_service.install_plugin(plugin)

    yield

    # clean-up
    with project.meltano_update() as meltano:
        meltano["plugins"]["models"] = [
            model_def
            for model_def in meltano["plugins"]["models"]
            if model_def["name"] not in MODELS
        ]

    for model in MODELS:
        shutil.rmtree(project.model_dir(model))


@pytest.fixture(scope="class")
def config_service(project):
    return ConfigService(project)


@pytest.fixture(scope="class")
def tap(config_service):
    tap = ProjectPlugin(PluginType.EXTRACTORS, "tap-mock")
    try:
        return config_service.add_to_file(tap)
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def target(config_service):
    target = ProjectPlugin(PluginType.LOADERS, "target-mock")
    try:
        return config_service.add_to_file(target)
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def dbt(config_service):
    dbt = ProjectPlugin(PluginType.TRANSFORMERS, "dbt")
    try:
        return config_service.add_to_file(dbt)
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def schedule_service(project, plugin_discovery_service):
    return ScheduleService(project, plugin_discovery_service=plugin_discovery_service)


@pytest.fixture(scope="class")
def schedule(project, tap, target, schedule_service):
    return schedule_service.add(
        None,
        "schedule-mock",
        extractor=tap.name,
        loader=target.name,
        transform="skip",
        interval="@once",
        start_date=datetime.datetime.now(),
    )


@pytest.fixture(scope="class")
def elt_context_builder(project, config_service, plugin_discovery_service):
    return ELTContextBuilder(
        project,
        config_service=config_service,
        plugin_discovery_service=plugin_discovery_service,
    )


@pytest.fixture(scope="class")
def job_logging_service(project):
    return JobLoggingService(project)


@pytest.fixture(scope="class")
def project(test_dir, project_init_service):
    project = project_init_service.init(add_discovery=True)
    logging.debug(f"Created new project at {project.root}")

    # empty out the `plugins`
    with project.meltano_update() as meltano:
        meltano.plugins = Canonical()

    # cd into the new project root
    os.chdir(project.root)

    yield project

    # clean-up
    Project.deactivate()
    os.chdir(test_dir)
    shutil.rmtree(project.root)
    logging.debug(f"Cleaned project at {project.root}")
