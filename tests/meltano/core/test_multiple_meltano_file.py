import os
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest
import yaml
from meltano.core.multiple_meltano_file import (
    INCLUDE_PATHS_KEY,
    contains_component,
    deep_get,
    deep_set,
    empty_components,
    get_included_config_file_component_names,
    get_included_config_file_components,
    get_included_config_file_path_names,
    get_included_directories,
    merge_components,
    pop_config_file_data,
    pop_updated_components,
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

# Sample Schedules
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

# TODO Sample Transforms

# Alpha
alpha_extractors = [tap_gitlab, tap_facebook, tap_zoom]
alpha_loaders = [target_csv, target_another]
alpha_schedules = [gitlab_to_csv, another_schedule]

# Beta
beta_extractors = [tap_gitlab, tap_facebook, tap_zoom]
beta_loaders = [target_csv, target_another]
beta_schedules = [gitlab_to_csv, another_schedule]

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
        "transforms": [],
        "models": [],
        "dashboards": [],
        "orchestrators": [],
        "transformers": [],
        "files": [],
        "utilities": [],
    },
    "schedules": [],
}


def build_directories(base: str, directories: List[str]):
    """
    Given an absolute path and a list of directory names, create a directory for each name at the absolute path.
    Return the absolute paths of each directory created.
    """
    absolute_directories = []
    base = Path(base)
    for directory in directories:
        directory_path = base.joinpath(directory)
        os.mkdir(directory_path)
        absolute_directories.append(str(directory_path))
    return absolute_directories


def build_files(directory: str, file_names: List[str]):
    for file_name in file_names:
        file_abs_path = os.path.join(directory, file_name)
        f = open(file_abs_path, "w")
        f.close()


class TestMultipleMeltanoFile:

    # TODO test_load

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

    def test_deep_set(self):
        actual_dict = {
            "one": {
                "two": {
                    "three": {"four_levels": 4},
                    "another_three": 3,
                },
                "another_two": 2,
            },
            "another_one": 1,
        }
        key = "one.two.three.four_levels"
        deep_set(actual_dict, key, 5)
        expected_dict = {
            "one": {
                "two": {
                    "three": {"four_levels": 5},
                    "another_three": 3,
                },
                "another_two": 2,
            },
            "another_one": 1,
        }

        assert actual_dict == expected_dict

    def test_deep_set_no_nest(self):
        actual_dict = {"one": "replace_me"}
        key = "one"
        deep_set(actual_dict, key)
        expected_dict = {"one": []}

        assert actual_dict == expected_dict

    def test_deep_set_custom_value(self):
        actual_dict = {}
        key = "one.two.three.four_levels"
        deep_set(actual_dict, key, 5)
        expected_dict = {"one": {"two": {"three": {"four_levels": 5}}}}

        assert actual_dict == expected_dict

    def test_deep_set_non_existing_keys(self):
        actual_dict = {}
        key = "one.two.three.four_levels"
        deep_set(actual_dict, key)
        expected_dict = {"one": {"two": {"three": {"four_levels": []}}}}

        assert actual_dict == expected_dict

    # TODO test_deep_pop

    # TODO test_pop_keys

    def test_empty_components(self):
        assert empty_components() == expected_empty_config

    def test_contains_component_has(self):
        status = contains_component(expected_updated_extractors, tap_zoom)
        assert status is True

    def test_contains_component_does_not_have(self):
        status = contains_component(expected_updated_extractors, extra_tap)
        assert status is False

    def test_contains_component_empty_list(self):
        status = contains_component([], extra_tap)
        assert status is False

    # TODO test_populate_components

    # TODO test_clean_components

    def test_get_included_directories_valid(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["a_subdirectory", "another_subdirectory"]
            meltano_config = {
                INCLUDE_PATHS_KEY: directories,
                "project_root": project_root,
            }

            # Build expected directories
            expected_directories = build_directories(project_root, directories)

            actual_directories = get_included_directories(meltano_config)

            assert actual_directories == expected_directories

    def test_get_included_directories_dir_dne(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["a_subdirectory", "another_subdirectory"]
            meltano_config = {
                INCLUDE_PATHS_KEY: directories + ["this_subdirectory_DNE"],
                "project_root": project_root,
            }

            # Build directories
            build_directories(project_root, directories)

            with pytest.raises(Exception) as exception:
                get_included_directories(meltano_config)

            assert "Invalid Included Path" == str(exception.value)

    def test_get_included_directories_abs_path(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["a_subdirectory", "another_subdirectory"]
            meltano_config = {
                INCLUDE_PATHS_KEY: directories + ["/absolute/path/directory/that_DNE"],
                "project_root": project_root,
            }

            # Build directories
            build_directories(project_root, directories)

            with pytest.raises(Exception) as exception:
                get_included_directories(meltano_config)

            assert "Invalid Included Path" == str(exception.value)

    def test_get_included_directories_project_root(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["./"]
            meltano_config = {
                INCLUDE_PATHS_KEY: directories,
                "project_root": project_root,
            }

            with pytest.raises(Exception) as exception:
                get_included_directories(meltano_config)

            assert "Invalid Included Path" == str(exception.value)

    def test_get_included_config_file_path_names_extension(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["a_subdirectory"]
            files = [
                "file1.YAML",
                "file2.yml",
                "file3.yaml",
                "file4.YML",
                "file5.YaMl",
                "file..yaml",
                "fileYAML",
                "yml.file",
                "file",
                ".YAML",
                ".file.yaml",
                "..yaml",
            ]

            # Build directories
            directories = build_directories(project_root, directories)

            # Build files
            build_files(directories[0], files)

            expected_included_config_file_path_names = [
                str(os.path.join(directories[0], ".file.yaml")),
                str(os.path.join(directories[0], "file..yaml")),
                str(os.path.join(directories[0], "file1.YAML")),
                str(os.path.join(directories[0], "file2.yml")),
                str(os.path.join(directories[0], "file3.yaml")),
                str(os.path.join(directories[0], "file4.YML")),
                str(os.path.join(directories[0], "file5.YaMl")),
            ]

            actual_included_config_file_path_names = (
                get_included_config_file_path_names(directories)
            )

            assert (
                actual_included_config_file_path_names
                == expected_included_config_file_path_names
            )

    def test_get_included_config_file_path_names_order(self):
        with tempfile.TemporaryDirectory() as project_root:
            directories = ["a_subdirectory"]
            files = [
                "_.yml",
                "..yml",
                "2.yml",
                "a.yml",
                "Z.yml",
            ]

            # Build directories
            directories = build_directories(project_root, directories)

            # Build files
            build_files(directories[0], files)

            expected_included_config_file_path_names = [
                str(os.path.join(directories[0], "2.yml")),
                str(os.path.join(directories[0], "Z.yml")),
                str(os.path.join(directories[0], "_.yml")),
                str(os.path.join(directories[0], "a.yml")),
            ]

            actual_included_config_file_path_names = (
                get_included_config_file_path_names(directories)
            )

            assert (
                actual_included_config_file_path_names
                == expected_included_config_file_path_names
            )

    def test_get_included_config_file_components(self):
        with tempfile.TemporaryDirectory() as directory:
            loaders = [nameless_target, target_csv]
            extractors = [tap_zoom]

            # Structure and uniqueness don't matter for the function being tested
            config1 = {"extractors": extractors, "loaders": loaders}
            config2 = {"extractors": extractors, "loaders": loaders}
            config_file_path_names = [
                os.path.join(directory, "config1.yml"),
                os.path.join(directory, "config2.yml"),
            ]

            file1 = open(config_file_path_names[0], "w")
            file2 = open(config_file_path_names[1], "w")
            yaml.dump(config1, file1)
            yaml.dump(config2, file2)
            file1.close()
            file2.close()

            actual_config_file_components = get_included_config_file_components(
                config_file_path_names
            )

            expected_config_file_components = {
                config_file_path_names[0]: config1,
                config_file_path_names[1]: config2,
            }

            assert actual_config_file_components == expected_config_file_components

    def test_get_included_config_file_components_empty(self):
        config_file_path_names = []
        expected_config_file_components: Dict[str, dict] = {}
        actual_config_file_components = get_included_config_file_components(
            config_file_path_names
        )

        assert actual_config_file_components == expected_config_file_components

    def test_get_included_config_file_component_names(self):
        loaders = [target_csv]
        extractors = [tap_zoom, tap_gitlab]
        config = {"plugins": {"extractors": extractors, "loaders": loaders}}
        config_file_components = {"config_path_name": config}

        actual_config_file_component_names = get_included_config_file_component_names(
            config_file_components
        )
        expected_config_file_component_names = {
            "config_path_name": {
                "plugins": {
                    "extractors": ["tap-zoom", "tap-gitlab"],
                    "loaders": ["target-csv"],
                    "transforms": [],
                    "models": [],
                    "dashboards": [],
                    "orchestrators": [],
                    "transformers": [],
                    "files": [],
                    "utilities": [],
                },
                "schedules": [],
            }
        }

        assert (
            actual_config_file_component_names == expected_config_file_component_names
        )

    def test_get_included_config_file_component_names_unnamed(self):
        loaders = [nameless_target]
        config = {"plugins": {"loaders": loaders}}
        config_file_components = {"config_path_name": config}

        with pytest.raises(Exception) as exception:
            get_included_config_file_component_names(config_file_components)

        assert "Unnamed Component" == str(exception.value)

    def test_merge_components(self):
        loaders = [target_csv]
        extractors = [tap_zoom, tap_gitlab]
        main_extractors = [tap_facebook, extra_tap]
        config = {"plugins": {"extractors": extractors, "loaders": loaders}}
        main_config = {
            "plugins": {"extractors": main_extractors, "loaders": []},
            "schedules": [],
        }
        config_file_components = {"config_path_name": config}

        actual_merged_components = merge_components(main_config, config_file_components)
        expected_merged_components = {
            "plugins": {
                "extractors": [tap_facebook, extra_tap, tap_zoom, tap_gitlab],
                "loaders": [target_csv],
            },
            "schedules": [],
        }

        assert actual_merged_components == expected_merged_components

    def test_merge_components_duplicate(self):
        loaders = [target_csv]
        config = {"plugins": {"loaders": loaders}}
        main_config = {"plugins": {"loaders": loaders}}

        config_file_components = {"config_path_name": config}

        with pytest.raises(Exception) as exception:
            merge_components(main_config, config_file_components)

        assert "Duplicate Component" == str(exception.value)

    def test_pop_updated_components(self):
        extractors = [tap_zoom, tap_gitlab]
        main_extractors = [tap_facebook, extra_tap]
        main_config = {
            "plugins": {"extractors": main_extractors + extractors, "loaders": []},
            "schedules": [],
        }
        config_file_component_names = {
            "config_path_name": {
                "plugins": {
                    "extractors": ["tap-zoom", "tap-gitlab"],
                    "loaders": ["target-csv"],
                }
            }
        }

        expected_leftover_main = {
            "plugins": {"extractors": main_extractors, "loaders": []},
            "schedules": [],
        }
        expected_popped_components = {
            "plugins": {
                "extractors": extractors,
                "loaders": [],
                "transforms": [],
                "models": [],
                "dashboards": [],
                "orchestrators": [],
                "transformers": [],
                "files": [],
                "utilities": [],
            },
            "schedules": [],
        }

        actual_popped_components = pop_updated_components(
            main_config, "config_path_name", config_file_component_names
        )

        assert main_config == expected_leftover_main
        assert actual_popped_components == expected_popped_components

    def test_pop_config_file_data_is_main(self):
        extractors = [tap_zoom, tap_gitlab]
        main_config = {
            "version": 1,
            "plugins": {"extractors": extractors, "loaders": []},
            "schedules": [],
        }
        expected_leftover_main = {
            "version": 1,
            "plugins": {"extractors": extractors},
        }

        actual_leftover_main = pop_config_file_data(
            main_config, "/path/name/doesnt/matter/", {}, True
        )

        assert actual_leftover_main == expected_leftover_main

    def test_pop_config_file_data_not_main(self):
        extractors = [tap_zoom, tap_gitlab]
        main_extractors = [tap_facebook, extra_tap]
        config_file_component_names = {
            "config_path_name": {
                "plugins": {
                    "extractors": ["tap-zoom", "tap-gitlab"],
                    "loaders": ["target-csv"],
                }
            }
        }
        main_config = {
            "version": 1,
            "plugins": {"extractors": main_extractors + extractors, "loaders": []},
            "schedules": [],
        }
        expected_leftover_main = {
            "version": 1,
            "plugins": {"extractors": main_extractors},
        }
        expected_popped_config = {
            "plugins": {"extractors": extractors},
        }

        actual_leftover_main = pop_config_file_data(
            main_config, "/path/name/doesnt/matter/", {}, True
        )
        actual_popped_config = pop_config_file_data(
            main_config, "config_path_name", config_file_component_names, False
        )

        assert actual_leftover_main == expected_leftover_main
        assert actual_popped_config == expected_popped_config
