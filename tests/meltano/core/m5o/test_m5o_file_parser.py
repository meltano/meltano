import pytest
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser


class TestMeltanoAnalysisFileParser:
    @pytest.fixture
    def subject(self, project):
        models_dir = project.root.joinpath("model")
        return MeltanoAnalysisFileParser(models_dir)

    def test_parse(self, subject):
        topics = subject.parse()

        assert len(topics) == 2

        for topic in topics:
            if topic["name"] == "carbon":
                assert len(topic["designs"]) == 1

            elif topic["name"] == "sfdc":
                assert len(topic["designs"]) == 1

    def test_compile(self, project, subject):
        topics = subject.parse()
        subject.compile(topics)

        assert project.root.joinpath("model/topics.index.m5oc").exists()
        assert project.root.joinpath("model/carbon.topic.m5oc").exists()
        assert project.root.joinpath("model/sfdc.topic.m5oc").exists()
