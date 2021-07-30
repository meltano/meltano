# import os
#
# import pytest
# import yaml
from meltano.core.multiple_meltano_file import (  # MultipleMeltanoFile,; get_included_config_file_component_names,; get_included_config_file_components,; get_included_config_file_paths,; get_included_directories,; load,; merge_components,; pop_updated_components,
    contains_component,
    deep_get,
    empty_meltano_components,
)

# Sample Extractors
tap_gitlab = {
    "name": "tap-gitlab",
    "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
}
tap_facebook = {
    "name": "tap-facebook",
    "variant": "meltano",
    "pip_url": "git+https://gitlab.com/meltano/tap-facebook.git",
}
tap_zoom = {
    "name": "tap-zoom",
    "variant": "mashey",
    "pip_url": "git+https://github.com/mashey/tap-zoom.git",
}
extra_tap = {"name": "extra-tap"}

# Sample Loaders
target_csv = {
    "name": "target-csv",
    "pip_url": "git+https://gitlab.com/meltano/target-csv.git",
}
target_another = {
    "name": "target-another",
    "pip_url": "another_url",
}
nameless_target = {
    "pip_url": "another_url",
}

# Sample schedules
gitlab_to_csv = {
    "name": "gitlab-to-csv",
    "extractor": "tap-gitlab",
    "loader": "target-csv",
    "transform": "skip",
}
another_schedule = {
    "name": "another-schedule",
    "extractor": "tap-zoom",
    "loader": "target-another",
    "transform": "skip",
}

# Sample transforms
# TODO

# Expected Meltano config
expected_updated_extractors = [tap_gitlab, tap_facebook, tap_zoom]
expected_updated_loaders = [target_csv, target_another]
expected_updated_schedules = [gitlab_to_csv, another_schedule]
expected_updated_config = {
    "version": 1,
    "send_anonymous_usage_stats": False,
    "project_id": "a_serial_number",
    "plugins": {
        "extractors": expected_updated_extractors,
        "loaders": expected_updated_loaders,
    },
    "schedules": expected_updated_schedules,
}

# Expected empty config
expected_empty_config = {
    "plugins": {
        "extractors": [],
        "loaders": [],
    },
    "schedules": [],
    "transforms": [],
}


class TestMultipleMeltanoFile:
    # TODO test load

    def test_deep_get_first_layer_existing_key(self):
        existing_key = "schedules"
        value = deep_get(expected_empty_config, existing_key)
        assert value == []

    def test_deep_get_first_layer_non_existing_key(self):
        non_existing_key = "non_existing_key"
        value = deep_get(expected_empty_config, non_existing_key)
        assert value is None

    def test_deep_get_second_layer_existing_key(self):
        existing_key = "plugins.loaders"
        value = deep_get(expected_empty_config, existing_key)
        assert value == []

    def test_deep_get_second_layer_non_existing_key(self):
        non_existing_key = "plugins.non_existing_key"
        value = deep_get(expected_empty_config, non_existing_key)
        assert value is None

    def test_empty_meltano_components(self):
        assert empty_meltano_components() == expected_empty_config

    def test_contains_component_has(self):
        status = contains_component(expected_updated_extractors, tap_zoom)
        assert status is True

    def test_contains_component_does_not_have(self):
        status = contains_component(expected_updated_extractors, extra_tap)
        assert status is False

    def test_contains_component_empty_list(self):
        status = contains_component([], extra_tap)
        assert status is False
