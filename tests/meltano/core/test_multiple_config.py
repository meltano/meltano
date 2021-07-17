import pytest
from meltano.core.multiple_config import MultipleConfigService

# TODO
#   secondary dump
#   control dictionary
#   secondary cleanup


class TestMultipleConfig:
    @pytest.fixture
    def subject(self, project):
        return MultipleConfigService(project.meltanofile)

    @pytest.fixture
    def control(self):
        return MultipleConfigService()

    @pytest.fixture
    def build_secondaries(self, subject: MultipleConfigService):
        # TODO
        #   find the path of the project
        #   create directories relative to it
        #   write prebuilt dumps in directories

        # Find path
        # project_path = subject.primary
        # project_directory = # Extract from Path object
        return None  # to satisfy linter

    def test_default_init_should_not_fail(self, subject):
        assert subject

    # def test_multiple_config(self, subject: MultipleConfigService, control: MultipleConfigService):
    #     control_meltano = control.load_meltano_read()
    #     experiment_meltano = subject.load_meltano_read()
    #     experiment_meltano.pop("secondary_configs")
    #
    #     try:
    #         # General
    #         # Same number of keys, keys are identical
    #         assert len(experiment_meltano) == len(control_meltano)
    #         assert experiment_meltano.keys() == control_meltano.keys()
    #
    #         # Extractors
    #         # Same number of extractors, extractors are identical
    #         control_extractors = control_meltano['plugins']['extractors']
    #         experiment_extractors = experiment_meltano['plugins']['extractors']
    #         assert len(experiment_extractors) == len(control_extractors)
    #         for extractor in control_extractors:
    #             assert extractor in experiment_extractors
    #
    #         # Loaders
    #         # Same number of loaders, loaders are identical
    #         control_loaders = control_meltano['plugins']['loaders']
    #         experiment_loaders = experiment_meltano['plugins']['loaders']
    #         assert len(experiment_loaders) == len(control_loaders)
    #         for loader in control_loaders:
    #             assert loader in experiment_loaders
    #
    #         # Schedules
    #         # Schedules are identical
    #         assert experiment_meltano['schedules'] == control_meltano['schedules']
    #
    #     except AssertionError:
    #         assert False
