import datetime
import itertools
import logging
import os
import shutil
from collections import namedtuple
from pathlib import Path

import pytest
import yaml

from meltano.core import bundle
from meltano.core.behavior.canonical import Canonical
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.config_service import ConfigService
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.environment_service import EnvironmentService
from meltano.core.job import Job, Payload, State
from meltano.core.logging.job_logging_service import JobLoggingService
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_files import ProjectFiles
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_plugins_service import (
    PluginAlreadyAddedException,
    ProjectPluginsService,
)
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.schedule_service import ScheduleAlreadyExistsError, ScheduleService
from meltano.core.state_service import StateService
from meltano.core.utils import merge

PROJECT_NAME = "a_meltano_project"


@pytest.fixture(scope="class")
def discovery():  # noqa: WPS213
    with bundle.find("discovery.yml").open() as base:
        discovery = yaml.safe_load(base)

    discovery[PluginType.EXTRACTORS].append(
        {
            "name": "tap-mock",
            "label": "Mock",
            "namespace": "tap_mock",
            "variants": [
                {
                    "name": "meltano",
                    "pip_url": "tap-mock",
                    "executable": "tap-mock",
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
                        {"name": "auth.username"},
                        {"name": "auth.password", "kind": "password"},
                    ],
                    "commands": {
                        "cmd": {
                            "args": "cmd meltano",
                            "description": "a description of cmd",
                        },
                        "cmd-variant": "cmd-variant meltano",
                        "test": {
                            "args": "--test",
                            "description": "Run tests",
                        },
                        "test_extra": {
                            "args": None,
                            "description": "Run extra tests",
                            "executable": "test-extra",
                        },
                    },
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

    discovery[PluginType.EXTRACTORS].append(
        {
            "name": "tap-mock-noinstall",
            "label": "Mock",
            "namespace": "tap_mock_noinstall",
            "variants": [
                {
                    "name": "meltano",
                    "executable": "tap-mock-noinstall",
                    "capabilities": ["discover", "catalog", "state"],
                    "settings": [
                        {"name": "test", "value": "mock"},
                        {"name": "start_date"},
                    ],
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

    discovery[PluginType.UTILITIES].append(
        {
            "name": "utility-mock",
            "namespace": "utility_mock",
            "pip_url": "utility-mock",
            "executable": "utility-mock",
            "commands": {
                "cmd": {
                    "args": "--option $ENV_VAR_ARG",
                    "description": "description of utility command",
                },
                "alternate-exec": {
                    "args": "--option $ENV_VAR_ARG",
                    "executable": "other-utility",
                },
                "containerized": {
                    "args": "",
                    "container_spec": {
                        "image": "mock-utils/mock",
                        "ports": {
                            "5000": "5000",
                        },
                        "volumes": ["$MELTANO_PROJECT_ROOT/example/:/usr/app/"],
                    },
                },
            },
        }
    )

    discovery[PluginType.MAPPERS].append(
        {
            "name": "mapper-mock",
            "namespace": "mapper_mock",
            "variants": [
                {
                    "name": "meltano",
                    "executable": "mapper-mock-cmd",
                    "pip_url": "mapper-mock",
                    "package_name": "mapper-mock",
                }
            ],
        }
    )

    return discovery


@pytest.fixture(scope="class")
def plugin_discovery_service(project, discovery):
    return PluginDiscoveryService(project, discovery=discovery)


@pytest.fixture(scope="class")
def project_compiler(project):
    return ProjectCompiler(project)


@pytest.fixture(scope="class")
def project_init_service():
    return ProjectInitService(PROJECT_NAME)


@pytest.fixture(scope="class")
def plugin_install_service(project, project_plugins_service):
    return PluginInstallService(project, plugins_service=project_plugins_service)


@pytest.fixture(scope="class")
def project_add_service(project, project_plugins_service):
    return ProjectAddService(project, plugins_service=project_plugins_service)


@pytest.fixture(scope="class")
def plugin_settings_service_factory(project, project_plugins_service):
    def _factory(plugin, **kwargs):
        return PluginSettingsService(
            project, plugin, plugins_service=project_plugins_service, **kwargs
        )

    return _factory


@pytest.fixture(scope="class")
def plugin_invoker_factory(
    project, project_plugins_service, plugin_settings_service_factory
):
    def _factory(plugin, **kwargs):
        return invoker_factory(
            project,
            plugin,
            plugins_service=project_plugins_service,
            plugin_settings_service=plugin_settings_service_factory(plugin),
            **kwargs,
        )

    return _factory


@pytest.fixture(scope="class")
def add_model(project, plugin_install_service, project_add_service):
    models = [
        "model-carbon-intensity",
        "model-gitflix",
        "model-salesforce",
        "model-gitlab",
    ]

    for model in models:
        plugin = project_add_service.add(PluginType.MODELS, model)
        plugin_install_service.install_plugin(plugin)

    yield

    # clean-up
    with project.meltano_update() as meltano:
        meltano["plugins"]["models"] = [
            model_def
            for model_def in meltano["plugins"]["models"]
            if model_def["name"] not in models
        ]

    for created_model in models:
        shutil.rmtree(project.model_dir(created_model))


@pytest.fixture(scope="class")
def config_service(project):
    return ConfigService(project, use_cache=False)


@pytest.fixture(scope="class")
def project_plugins_service(project, config_service, plugin_discovery_service):
    return ProjectPluginsService(
        project,
        config_service=config_service,
        discovery_service=plugin_discovery_service,
        use_cache=False,
    )


@pytest.fixture(scope="class")
def tap(project_add_service):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS, "tap-mock", variant="meltano"
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def alternative_tap(project_add_service, tap):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock--singer-io",
            inherit_from=tap.name,
            variant="singer-io",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def inherited_tap(project_add_service, tap):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited",
            inherit_from=tap.name,
            commands={
                "cmd": "cmd inherited",
                "cmd-inherited": "cmd-inherited",
            },
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def nonpip_tap(project_add_service):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock-noinstall",
            executable="tap-mock-noinstall",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def target(project_add_service):
    try:
        return project_add_service.add(PluginType.LOADERS, "target-mock")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def alternative_target(project_add_service):
    # We don't load the `target` fixture here since this ProjectPlugin should
    # have a BasePlugin parent, not the `target` ProjectPlugin
    try:
        return project_add_service.add(
            PluginType.LOADERS, "target-mock-alternative", inherit_from="target-mock"
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def dbt(project_add_service):
    try:
        return project_add_service.add(PluginType.TRANSFORMERS, "dbt")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def utility(project_add_service):
    try:
        return project_add_service.add(PluginType.UTILITIES, "utility-mock")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def schedule_service(project, project_plugins_service):
    return ScheduleService(project, plugins_service=project_plugins_service)


@pytest.fixture(scope="class")
def schedule(project, tap, target, schedule_service):
    try:
        return schedule_service.add(
            None,
            "schedule-mock",
            extractor=tap.name,
            loader=target.name,
            transform="skip",
            interval="@once",
            start_date=datetime.datetime.now(),
        )
    except ScheduleAlreadyExistsError as err:
        return err.schedule


@pytest.fixture(scope="function")
def environment_service(project):
    service = EnvironmentService(project)
    yield service

    # Cleanup: remove any added Environments
    for environment in service.list_environments():
        service.remove(environment.name)


@pytest.fixture(scope="class")
def elt_context_builder(project, project_plugins_service):
    return ELTContextBuilder(project, plugins_service=project_plugins_service)


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

    ProjectSettingsService(project).set("snowplow.collector_endpoints", "[]")

    # cd into the new project root
    os.chdir(project.root)

    yield project

    # clean-up
    Project.deactivate()
    os.chdir(test_dir)
    shutil.rmtree(project.root)
    logging.debug(f"Cleaned project at {project.root}")


@pytest.fixture(scope="class")
def project_files(test_dir, compatible_copy_tree):
    project_init_service = ProjectInitService("a_multifile_meltano_project_core")
    project = project_init_service.init(add_discovery=False)
    logging.debug(f"Created new project at {project.root}")

    current_dir = Path(__file__).parent
    multifile_project_root = current_dir.joinpath("multifile_project/")

    os.remove(project.meltanofile)
    compatible_copy_tree(multifile_project_root, project.root)
    # cd into the new project root
    os.chdir(project.root)

    yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)

    # clean-up
    Project.deactivate()
    os.chdir(test_dir)
    shutil.rmtree(project.root)
    logging.debug(f"Cleaned project at {project.root}")


@pytest.fixture(scope="class")
def mapper(project_add_service):
    try:
        return project_add_service.add(
            PluginType.MAPPERS,
            "mapper-mock",
            variant="meltano",
            mappings=[
                {
                    "name": "mock-mapping-0",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email",
                                "tap_stream_name": "commits",
                                "type": "MASK-HIDDEN",
                            }
                        ]
                    },
                },
                {
                    "name": "mock-mapping-1",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "given_name",
                                "tap_stream_name": "users",
                                "type": "lowercase",
                            }
                        ]
                    },
                },
            ],
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


def create_job_id(description: str, env: str = "dev") -> str:
    return f"{env}:tap-{description}-to-target-{description}"


@pytest.fixture
def num_params():
    return 10


@pytest.fixture
def payloads(num_params):
    mock_payloads_dict = {
        "mock_state_payloads": [
            {
                "singer_state": {
                    f"bookmark-{idx_i}": idx_i + idx_j for idx_j in range(num_params)
                }
            }
            for idx_i in range(num_params)
        ],
        "mock_error_payload": {"error": "failed"},
        "mock_empty_payload": {},
    }
    payloads = namedtuple("payloads", mock_payloads_dict)
    return payloads(**mock_payloads_dict)


@pytest.fixture
def job_ids(num_params):
    job_id_dict = {
        "single_incomplete_job_id": create_job_id("single-incomplete"),
        "single_complete_job_id": create_job_id("single-complete"),
        "multiple_incompletes_job_id": create_job_id("multiple-incompletes"),
        "multiple_completes_job_id": create_job_id("multiple-completes"),
        "single_complete_then_multiple_incompletes_job_id": create_job_id(
            "single-complete-then-multiple-incompletes"
        ),
        "single_incomplete_then_multiple_completes_job_id": create_job_id(
            "single-incomplete-then-multiple-completes"
        ),
    }
    job_ids = namedtuple("job_ids", job_id_dict)
    return job_ids(**job_id_dict)


@pytest.fixture
def mock_time():
    def _mock_time():
        for idx in itertools.count():  # noqa: WPS526
            yield datetime.datetime(1, 1, 1) + datetime.timedelta(hours=idx)

    return _mock_time()


@pytest.fixture()
def job_args():
    job_args_dict = {
        "complete_job_args": {"state": State.SUCCESS, "payload_flags": Payload.STATE},
        "incomplete_job_args": {
            "state": State.FAIL,
            "payload_flags": Payload.INCOMPLETE_STATE,
        },
    }
    job_args = namedtuple("job_args", job_args_dict)
    return job_args(**job_args_dict)


@pytest.fixture
def job_ids_with_jobs(job_ids, job_args, payloads, mock_time):
    jobs = {
        job_ids.single_incomplete_job_id: [
            Job(
                job_id=job_ids.single_incomplete_job_id,
                **job_args.incomplete_job_args,
                payload=payloads.mock_state_payloads[0],
            )
        ],
        job_ids.single_complete_job_id: [
            Job(
                job_id=job_ids.single_complete_job_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            )
        ],
        job_ids.multiple_incompletes_job_id: [
            Job(
                job_id=job_ids.multiple_incompletes_job_id,
                **job_args.incomplete_job_args,
                payload=payload,
            )
            for payload in payloads.mock_state_payloads
        ],
        job_ids.multiple_completes_job_id: [
            Job(
                job_id=job_ids.multiple_completes_job_id,
                payload=payload,
                **job_args.complete_job_args,
            )
            for payload in payloads.mock_state_payloads
        ],
        job_ids.single_complete_then_multiple_incompletes_job_id: [
            Job(
                job_id=job_ids.single_complete_then_multiple_incompletes_job_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            )
        ]
        + [
            Job(
                job_id=job_ids.single_complete_then_multiple_incompletes_job_id,
                payload=payload,
                **job_args.incomplete_job_args,
            )
            for payload in payloads.mock_state_payloads[1:]
        ],
        job_ids.single_incomplete_then_multiple_completes_job_id: [
            Job(
                job_id=job_ids.single_incomplete_then_multiple_completes_job_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.incomplete_job_args,
            )
        ]
        + [
            Job(
                job_id=job_ids.single_incomplete_then_multiple_completes_job_id,
                payload=payload,
                **job_args.complete_job_args,
            )
            for payload in payloads.mock_state_payloads[1:]
        ],
    }
    for job_list in jobs.values():
        for job in job_list:
            job.started_at = next(mock_time)
            job.ended_at = next(mock_time)
    return jobs


@pytest.fixture
def jobs(job_ids_with_jobs):
    return [job for job_list in job_ids_with_jobs.values() for job in job_list]


@pytest.fixture
def job_ids_with_expected_states(job_ids, payloads, job_ids_with_jobs):  # noqa: WPS210
    final_state = {}
    for state in payloads.mock_state_payloads:
        merge(state, final_state)
    expectations = {
        job_ids.single_complete_job_id: payloads.mock_state_payloads[0],
        job_ids.single_incomplete_job_id: payloads.mock_empty_payload,
    }

    for job_id, job_list in job_ids_with_jobs.items():
        expectations[job_id] = {}

        complete_jobs = []
        incomplete_jobs = []
        dummy_jobs = []
        # Get latest complete non-dummy job.
        for job in job_list:
            if job.state == State.STATE_EDIT:
                dummy_jobs.append(job)
            elif job.payload_flags == Payload.STATE:
                complete_jobs.append(job)
            elif job.payload_flags == Payload.INCOMPLETE_STATE:
                incomplete_jobs.append(job)
        latest_complete_job = None
        if complete_jobs:
            latest_complete_job = max(complete_jobs, key=lambda _job: _job.ended_at)
        # Get all incomplete jobs since latest complete non-dummy job.
        latest_incomplete_job = None
        if incomplete_jobs:
            latest_incomplete_job = max(incomplete_jobs, key=lambda _job: _job.ended_at)
        if latest_complete_job:
            expectations[job_id] = merge(
                expectations[job_id], latest_complete_job.payload
            )

        for job in incomplete_jobs:
            if (not latest_complete_job) or (
                job.ended_at > latest_complete_job.ended_at
            ):
                expectations[job_id] = merge(expectations[job_id], job.payload)
        # Get all dummy jobs since latest non-dummy job.
        for job in dummy_jobs:
            if (
                not latest_complete_job or (job.ended_at > latest_complete_job.ended_at)
            ) and (
                (not latest_incomplete_job)
                or (job.ended_at > latest_incomplete_job.ended_at)
            ):
                expectations[job_id] = merge(expectations[job_id], job.payload)
    return [
        (test_job_id, expected_state)
        for test_job_id, expected_state in expectations.items()
    ]


@pytest.fixture
def job_history_session(jobs, session):
    for job in jobs:
        job.save(session)
    yield session


@pytest.fixture
def state_service(job_history_session):
    return StateService(session=job_history_session)


@pytest.fixture
def project_with_environment(project: Project) -> Project:
    project.activate_environment("dev")
    yield project
    project.active_environment = None
