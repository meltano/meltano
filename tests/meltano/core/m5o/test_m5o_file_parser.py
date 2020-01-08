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
                assert topic["namespace"] == "model-carbon-intensity"

            elif topic["name"] == "sfdc":
                assert len(topic["designs"]) == 1
                assert topic["namespace"] == "model-salesforce"

    def test_compile(self, project, add_model, subject):
        topics = subject.parse_packages()
        subject.compile(topics)

        models = project.run_dir("models")
        subfolders = [f.name for f in models.glob("**/*") if f.is_dir()]
        compiled = [f.name for f in models.glob("**/*.topic.m5oc")]

        assert "model-gitflix" in subfolders
        assert "gitflix.topic.m5oc" in compiled
        assert "model-carbon-intensity" in subfolders
        assert "carbon.topic.m5oc" in compiled
        assert "model-salesforce" in subfolders
        assert "sfdc.topic.m5oc" in compiled
