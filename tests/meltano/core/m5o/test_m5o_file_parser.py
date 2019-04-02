import pytest
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser


class TestMeltanoAnalysisFileParser:
    @pytest.fixture
    def subject(self, project):
        return MeltanoAnalysisFileParser(project)

    def test_parse(self, add_model, subject):
        topics = subject.parse_packages()

        assert len(topics) == 4

        for topic in topics:
            if topic["name"] == "carbon":
                assert len(topic["designs"]) == 1

            elif topic["name"] == "sfdc":
                assert len(topic["designs"]) == 1

    def test_compile(self, project, add_model, subject):
        topics = subject.parse()
        subject.compile(topics)

        models = [f.parts[-1] for f in project.model_dir().iterdir()]

        assert "model-gitflix" in models
        assert "model-carbon-intensity-sqlite" in models
        assert "model-salesforce" in models
