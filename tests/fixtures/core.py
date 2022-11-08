from __future__ import annotations

import datetime
import itertools
import logging
import os
from collections import defaultdict, namedtuple
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from fixtures.utils import tmp_project
from meltano.core import bundle
from meltano.core.behavior.canonical import Canonical
from meltano.core.config_service import ConfigService
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.environment_service import EnvironmentService
from meltano.core.job import Job, Payload, State
from meltano.core.job_state import JobState
from meltano.core.logging.job_logging_service import JobLoggingService
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_discovery_service import (
    LockedDefinitionService,
    PluginDiscoveryService,
)
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
from meltano.core.task_sets_service import TaskSetsService
from meltano.core.utils import merge

current_dir = Path(__file__).parent


@pytest.fixture(scope="class")
def discovery():  # noqa: WPS213
    with open(bundle.root / "discovery.yml") as base:
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
                        {"name": "boolean", "kind": "boolean"},
                        {"name": "auth.username"},
                        {"name": "auth.password", "kind": "password"},
                        {
                            "name": "aliased",
                            "kind": "string",
                            "aliases": ["aliased_1", "aliased_2", "aliased_3"],
                        },
                        {"name": "stacked_env_var", "kind": "string"},
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
                            "args": "test_extra",
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
            "settings": [
                {
                    "name": "schema",
                    "env": "MOCKED_SCHEMA",
                }
            ],
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
            "requires": {
                "files": [
                    {
                        "name": "files-transformer-mock",
                        "variant": "meltano",
                    },
                ],
            },
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
                },
                {
                    "name": "alternative",
                    "executable": "mapper-mock-alt",
                    "pip_url": "mapper-mock-alt",
                    "package_name": "mapper-mock-alt",
                },
            ],
        }
    )

    return discovery


@pytest.fixture(scope="class")
def plugin_discovery_service(project, discovery):
    return PluginDiscoveryService(project, discovery=deepcopy(discovery))


@pytest.fixture(scope="class")
def locked_definition_service(project):
    return LockedDefinitionService(project)


@pytest.fixture(scope="class")
def project_init_service(request):
    return ProjectInitService(f"project_{request.node.name}")


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
def config_service(project):
    return ConfigService(project, use_cache=False)


@pytest.fixture(scope="class")
def project_plugins_service(
    project,
    config_service,
    plugin_discovery_service,
    meltano_hub_service,
):
    return ProjectPluginsService(
        project,
        config_service=config_service,
        discovery_service=plugin_discovery_service,
        hub_service=meltano_hub_service,
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
def transformer(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(PluginType.TRANSFORMERS, "transformer-mock")
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
def task_sets_service(project):
    return TaskSetsService(project)


@pytest.fixture(scope="class")
def elt_schedule(project, tap, target, schedule_service):
    try:
        return schedule_service.add_elt(
            None,
            "elt-schedule-mock",
            extractor=tap.name,
            loader=target.name,
            transform="skip",
            interval="@once",
            start_date=datetime.datetime.now(),
        )
    except ScheduleAlreadyExistsError as err:
        return err.schedule


@pytest.fixture(scope="class")
def job_schedule(project, tap, target, schedule_service):
    try:
        return schedule_service.add(
            "job-schedule-mock",
            "mock-job",
            interval="@once",
        )
    except ScheduleAlreadyExistsError as err:
        return err.schedule


@pytest.fixture(scope="function")
def environment_service(project):
    service = EnvironmentService(project)
    try:
        yield service
    finally:
        # Remove any added Environments
        for environment in service.list_environments():
            service.remove(environment.name)


@pytest.fixture(scope="class")
def elt_context_builder(project, project_plugins_service):
    return ELTContextBuilder(project, plugins_service=project_plugins_service)


@pytest.fixture(scope="class")
def job_logging_service(project):
    return JobLoggingService(project)


@contextmanager
def project_directory(test_dir, project_init_service):
    project = project_init_service.init(add_discovery=True)
    logging.debug(f"Created new project at {project.root}")

    # empty out the `plugins`
    with project.meltano_update() as meltano:
        meltano.plugins = Canonical()

    ProjectSettingsService(project).set("snowplow.collector_endpoints", "[]")

    # cd into the new project root
    os.chdir(project.root)

    try:
        yield project
    finally:
        Project.deactivate()
        os.chdir(test_dir)
        logging.debug(f"Cleaned project at {project.root}")


@pytest.fixture(scope="class")
def project(test_dir, project_init_service):
    with project_directory(test_dir, project_init_service) as project:
        yield project


@pytest.fixture(scope="function")
def project_function(test_dir, project_init_service):
    with project_directory(test_dir, project_init_service) as project:
        yield project


@pytest.fixture(scope="class")
def project_files(test_dir, compatible_copy_tree):
    with tmp_project(
        "a_multifile_meltano_project_core",
        current_dir / "multifile_project",
        compatible_copy_tree,
    ) as project:
        yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)


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


def create_state_id(description: str, env: str = "dev") -> str:
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
def state_ids(num_params):
    state_id_dict = {
        "single_incomplete_state_id": create_state_id("single-incomplete"),
        "single_complete_state_id": create_state_id("single-complete"),
        "multiple_incompletes_state_id": create_state_id("multiple-incompletes"),
        "multiple_completes_state_id": create_state_id("multiple-completes"),
        "single_complete_then_multiple_incompletes_state_id": create_state_id(
            "single-complete-then-multiple-incompletes"
        ),
        "single_incomplete_then_multiple_completes_state_id": create_state_id(
            "single-incomplete-then-multiple-completes"
        ),
    }
    state_ids = namedtuple("state_ids", state_id_dict)
    return state_ids(**state_id_dict)


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
def state_ids_with_jobs(state_ids, job_args, payloads, mock_time):
    jobs = {
        state_ids.single_incomplete_state_id: [
            Job(
                job_name=state_ids.single_incomplete_state_id,
                **job_args.incomplete_job_args,
                payload=payloads.mock_state_payloads[0],
            )
        ],
        state_ids.single_complete_state_id: [
            Job(
                job_name=state_ids.single_complete_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            )
        ],
        state_ids.multiple_incompletes_state_id: [
            Job(
                job_name=state_ids.multiple_incompletes_state_id,
                **job_args.incomplete_job_args,
                payload=payload,
            )
            for payload in payloads.mock_state_payloads
        ],
        state_ids.multiple_completes_state_id: [
            Job(
                job_name=state_ids.multiple_completes_state_id,
                payload=payload,
                **job_args.complete_job_args,
            )
            for payload in payloads.mock_state_payloads
        ],
        state_ids.single_complete_then_multiple_incompletes_state_id: [
            Job(
                job_name=state_ids.single_complete_then_multiple_incompletes_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            )
        ]
        + [
            Job(
                job_name=state_ids.single_complete_then_multiple_incompletes_state_id,
                payload=payload,
                **job_args.incomplete_job_args,
            )
            for payload in payloads.mock_state_payloads[1:]
        ],
        state_ids.single_incomplete_then_multiple_completes_state_id: [
            Job(
                job_name=state_ids.single_incomplete_then_multiple_completes_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.incomplete_job_args,
            )
        ]
        + [
            Job(
                job_name=state_ids.single_incomplete_then_multiple_completes_state_id,
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
def jobs(state_ids_with_jobs):
    return [job for job_list in state_ids_with_jobs.values() for job in job_list]


@pytest.fixture
def state_ids_with_expected_states(  # noqa: WPS210
    state_ids, payloads, state_ids_with_jobs
):
    final_state = {}
    for state in payloads.mock_state_payloads:
        merge(state, final_state)
    expectations = {
        state_ids.single_complete_state_id: payloads.mock_state_payloads[0],
        state_ids.single_incomplete_state_id: payloads.mock_empty_payload,
    }

    for state_id, job_list in state_ids_with_jobs.items():
        expectations[state_id] = {}
        jobs = defaultdict(list)
        # Get latest complete non-dummy job.
        for job in job_list:
            if job.state == State.STATE_EDIT:
                jobs["dummy"].append(job)
            elif job.payload_flags == Payload.STATE:
                jobs["complete"].append(job)
            elif job.payload_flags == Payload.INCOMPLETE_STATE:
                jobs["incomplete"].append(job)
        latest_job = {
            kind: (
                max(jobs[kind], key=lambda _job: _job.ended_at) if jobs[kind] else None
            )
            for kind in ("complete", "incomplete")
        }
        if latest_job["complete"]:
            expectations[state_id] = merge(
                expectations[state_id], latest_job["complete"].payload
            )

        for job in jobs["incomplete"]:
            if (not latest_job["complete"]) or (
                job.ended_at > latest_job["complete"].ended_at
            ):
                expectations[state_id] = merge(expectations[state_id], job.payload)
        # Get all dummy jobs since latest non-dummy job.
        for job in jobs["dummy"]:
            if (
                not latest_job["complete"]
                or (job.ended_at > latest_job["complete"].ended_at)
            ) and (
                (not latest_job["incomplete"])
                or (job.ended_at > latest_job["incomplete"].ended_at)
            ):
                expectations[state_id] = merge(expectations[state_id], job.payload)
    return [
        (test_state_id, expected_state)
        for test_state_id, expected_state in expectations.items()
    ]


@pytest.fixture
def job_history_session(jobs, session):
    job: Job
    job_names = set()
    for job in jobs:
        job.save(session)
        job_names.add(job.job_name)
    for job_name in job_names:
        job_state = JobState.from_job_history(session, job_name)
        session.add(job_state)
    yield session


@pytest.fixture
def state_service(job_history_session, project):
    return StateService(project, session=job_history_session)


@pytest.fixture
def project_with_environment(project: Project):
    project.activate_environment("dev")
    project.active_environment.env[
        "ENVIRONMENT_ENV_VAR"
    ] = "${MELTANO_PROJECT_ROOT}/file.txt"
    try:
        yield project
    finally:
        project.active_environment = None
