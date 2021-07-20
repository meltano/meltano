import datetime
import os

import pytest
import yaml
from meltano.core.multiple_config import MultipleConfigService

# TODO further obfuscate testing content
dump0 = {
    "version": 1,
    "send_anonymous_usage_stats": False,
    "project_id": "35092b8c-ce7d-4af8-a4b5-7980f73e3280",
    "plugins": {
        "extractors": [
            {
                "name": "tap-jira",
                "pip_url": "-e extract/tap-jira",
                "config": {
                    "start_date": "2019-03-01",
                    "username": None,
                    "password": None,
                    "base_url": "https://jira.com",
                },
                "executable": "tap-jira",
                "capabilities": ["discover", "catalog"],
                "select": [
                    "issues.id",
                    "issues.key",
                    "issues.fields",
                    "issues.fields.assignee",
                    "issues.fields.created",
                    "issues.fields.duedate",
                    "issues.fields.issuetype",
                    "issues.fields.labels",
                    "issues.fields.lastViewed",
                    "issues.fields.priority",
                    "issues.fields.reporter",
                    "issues.fields.status",
                    "issues.fields.summary",
                    "issues.fields.updated",
                    "changelogs.*",
                ],
                "table_mappings": {
                    "issues": "jira_issues",
                    "changelogs": "jira_changelogs",
                },
            },
            {
                "name": "tap-nicedataexplorer",
                "pip_url": "extract/tap-nicedataexplorer",
                "config": {"api_url": "https://nde.nicecloudsvc.com/", "api_key": None},
                "executable": "tap-nicedataexplorer",
                "capabilities": ["catalog", "discover", "state"],
                "table_mappings": {
                    "agents": "nde_agents",
                    "activity_codes": "nde_activity_codes",
                    "acd": "nde_acd",
                    "person": "nde_person",
                    "activity_log_dtl": "nde_activity_log_dtl",
                    "agent_data_definition": "nde_agent_data_definition",
                    "agent_data_value_definition": "nde_agent_data_value_definition",
                    "agent_data_group_definition": "nde_agent_data_group_definition",
                    "agent_acd_logon": "nde_agent_acd_logon",
                    "agent_schedule_detail": "nde_agent_schedule_detail",
                    "agent_schedule": "nde_agent_schedule",
                    "activity_code_attr_assignment": "nde_activity_code_attr_assignment",
                    "activity_code_attr_value": "nde_activity_code_attr_value",
                },
            },
            {
                "name": "tap-starwars",
                "namespace": "tap_starwars",
                "pip_url": "-e extract/tap-starwars",
                "executable": "tap-starwars",
                "capabilities": ["catalog", "discover", "state"],
                "config": {"api_url": "http://swapi.dev/api"},
                "table_mappings": {"people": "starwars_people"},
            },
        ],
        "loaders": [
            {
                "name": "target-s3-jsonl",
                "pip_url": "-e load/target-s3-jsonl",
                "config": {
                    "s3_bucket": "data-lake-staging",
                    "s3_key_prefix": "developer/dev/integrations/",
                    "buffer_record_limit": 10000,
                },
                "executable": "target-s3-jsonl",
            },
            {
                "name": "target-s3-jsonl--edw",
                "inherit_from": "target-s3-jsonl",
                "label": "target-s3-jsonl--edw",
                "description": "EDW data loader of JSON Lines " "(JSONL) files",
            },
        ],
    },
    "schedules": [
        {
            "name": "jira-to-s3",
            "extractor": "tap-jira",
            "loader": "target-s3-jsonl--edw",
            "transform": "skip",
            "interval": "0 1 * * *",
            "start_date": datetime.datetime(2021, 3, 29, 0, 0),
        },
        {
            "name": "nicedataexplorer-to-s3",
            "extractor": "tap-nicedataexplorer",
            "loader": "target-s3-jsonl--edw",
            "transform": "skip",
            "interval": "0 9 * * *",
            "start_date": datetime.datetime(2021, 5, 4, 0, 0),
        },
    ],
}

dump1 = {
    "extractors": [
        {
            "name": "tap-zoom",
            "variant": "mashey",
            "pip_url": "git+https://github.com/mashey/tap-zoom.git",
        }
    ]
}

dump2 = {
    "loaders": [
        {
            "name": "target-s3-jsonl",
            "pip_url": "-e load/target-s3-jsonl",
            "config": [
                {
                    "s3_bucket": "data-lake-staging",
                    "s3_key_prefix": "developer/dev/integrations/",
                    "buffer_record_limit": "50000",
                }
            ],
            "executable": "target-s3-jsonl",
        }
    ]
}

dump3 = {
    "loaders": [
        {
            "name": "target-s3-jsonl--edw",
            "inherit_from": "target-s3-jsonl",
            "label": "target-s3-jsonl--edw",
            "description": "EDW data loader of JSON Lines (JSONL) files",
        }
    ]
}

dump4 = {
    "loaders": [
        {
            "name": "target-s3-jsonl--edw",
            "inherit_from": "target-s3-jsonl",
            "label": " the-wrong-label",
            "description": "EDW data loader of JSON Lines (JSONL) files",
        }
    ]
}

dump5 = {
    "version": 1,
    "send_anonymous_usage_stats": False,
    "project_id": "35092b8c-ce7d-4af8-a4b5-7980f73e3280",
    "plugins": {
        "extractors": [
            {
                "name": "tap-jira",
                "pip_url": "-e extract/tap-jira",
                "config": {
                    "start_date": "2019-03-01",
                    "username": None,
                    "password": None,
                    "base_url": "https://jira.com",
                },
                "executable": "tap-jira",
                "capabilities": ["discover", "catalog"],
                "select": [
                    "issues.id",
                    "issues.key",
                    "issues.fields",
                    "issues.fields.assignee",
                    "issues.fields.created",
                    "issues.fields.duedate",
                    "issues.fields.issuetype",
                    "issues.fields.labels",
                    "issues.fields.lastViewed",
                    "issues.fields.priority",
                    "issues.fields.reporter",
                    "issues.fields.status",
                    "issues.fields.summary",
                    "issues.fields.updated",
                    "changelogs.*",
                ],
                "table_mappings": {
                    "issues": "jira_issues",
                    "changelogs": "jira_changelogs",
                },
            },
            {
                "name": "tap-nicedataexplorer",
                "pip_url": "extract/tap-nicedataexplorer",
                "config": {"api_url": "https://nde.nicecloudsvc.com/", "api_key": None},
                "executable": "tap-nicedataexplorer",
                "capabilities": ["catalog", "discover", "state"],
                "table_mappings": {
                    "agents": "nde_agents",
                    "activity_codes": "nde_activity_codes",
                    "acd": "nde_acd",
                    "person": "nde_person",
                    "activity_log_dtl": "nde_activity_log_dtl",
                    "agent_data_definition": "nde_agent_data_definition",
                    "agent_data_value_definition": "nde_agent_data_value_definition",
                    "agent_data_group_definition": "nde_agent_data_group_definition",
                    "agent_acd_logon": "nde_agent_acd_logon",
                    "agent_schedule_detail": "nde_agent_schedule_detail",
                    "agent_schedule": "nde_agent_schedule",
                    "activity_code_attr_assignment": "nde_activity_code_attr_assignment",
                    "activity_code_attr_value": "nde_activity_code_attr_value",
                },
            },
            {
                "name": "tap-starwars",
                "namespace": "tap_starwars",
                "pip_url": "-e extract/tap-starwars",
                "executable": "tap-starwars",
                "capabilities": ["catalog", "discover", "state"],
                "config": {"api_url": "http://swapi.dev/api"},
                "table_mappings": {"people": "starwars_people"},
            },
            {
                "name": "tap-zoom",
                "variant": "mashey",
                "pip_url": "git+https://github.com/mashey/tap-zoom.git",
            },
        ],
        "loaders": [
            {
                "name": "target-s3-jsonl",
                "pip_url": "-e load/target-s3-jsonl",
                "config": {
                    "s3_bucket": "data-lake-staging",
                    "s3_key_prefix": "developer/dev/integrations/",
                    "buffer_record_limit": 10000,
                },
                "executable": "target-s3-jsonl",
            },
            {
                "name": "target-s3-jsonl--edw",
                "inherit_from": "target-s3-jsonl",
                "label": "target-s3-jsonl--edw",
                "description": "EDW data loader of JSON Lines " "(JSONL) files",
            },
        ],
    },
    "schedules": [
        {
            "name": "jira-to-s3",
            "extractor": "tap-jira",
            "loader": "target-s3-jsonl--edw",
            "transform": "skip",
            "interval": "0 1 * * *",
            "start_date": datetime.datetime(2021, 3, 29, 0, 0),
        },
        {
            "name": "nicedataexplorer-to-s3",
            "extractor": "tap-nicedataexplorer",
            "loader": "target-s3-jsonl--edw",
            "transform": "skip",
            "interval": "0 9 * * *",
            "start_date": datetime.datetime(2021, 5, 4, 0, 0),
        },
    ],
}

INCLUDE_PATHS = {
    "a_subdirectory": ["dump1.yml", "dump2.yml"],
    "another_subdirectory": ["dump3.yml", "dump4.yml"],
}

SECONDARY_CONFIGS = {
    "dump1.yml": dump1,
    "dump2.yml": dump2,
    "dump3.yml": dump3,
    "dump4.yml": dump4,
}

# Add include-paths
dump0["include-paths"] = []
for path in INCLUDE_PATHS:
    dump0["include-paths"].append(path)


class TestMultipleConfig:
    @pytest.fixture
    def subject(self, project):
        with open(project.meltanofile, "a") as file:
            file.write(yaml.dump(dump0))
        return MultipleConfigService(project.meltanofile)

    @pytest.fixture
    def control(self, project):
        control_config_path = project.root_dir("dump5.yml")
        with open(control_config_path, "w") as file:
            file.write(yaml.dump(dump5))
            file.close()
        return MultipleConfigService(control_config_path)

    @pytest.fixture
    def build_secondaries(self, subject: MultipleConfigService):
        #   find the path of the project
        project_root = subject.primary.parent

        #   create directories relative to it
        for path in INCLUDE_PATHS:
            full_path = project_root.joinpath(path)
            os.mkdir(full_path)
            #   write prebuilt dumps in directories
            for dump in INCLUDE_PATHS[path]:
                with open(full_path.joinpath(dump), "w") as file:
                    file.write(yaml.dump(SECONDARY_CONFIGS[dump]))
                    file.close()

    def test_default_init_should_not_fail(self, subject):
        assert subject

    # TODO check if root is in include-paths, whether primary contents are duplicated
    def test_multiple_config(
        self,
        subject: MultipleConfigService,
        control: MultipleConfigService,
        build_secondaries,
    ):
        control_meltano = control.load_meltano_read()
        experiment_meltano = subject.load_meltano_read()
        experiment_meltano.pop("include-paths")

        try:
            # General
            # Same number of keys, keys are identical
            assert len(experiment_meltano) == len(control_meltano)
            assert experiment_meltano.keys() == control_meltano.keys()

            # Extractors
            # Same number of extractors, extractors are identical
            control_extractors = control_meltano["plugins"]["extractors"]
            experiment_extractors = experiment_meltano["plugins"]["extractors"]
            assert len(experiment_extractors) == len(control_extractors)
            for extractor in control_extractors:
                assert extractor in experiment_extractors

            # Loaders
            # Same number of loaders, loaders are identical
            control_loaders = control_meltano["plugins"]["loaders"]
            experiment_loaders = experiment_meltano["plugins"]["loaders"]
            assert len(experiment_loaders) == len(control_loaders)
            for loader in control_loaders:
                assert loader in experiment_loaders

            # Schedules
            # Schedules are identical
            assert experiment_meltano["schedules"] == control_meltano["schedules"]

        except AssertionError:
            assert False
