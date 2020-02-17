import pytest
import yaml

from meltano.core.meltano_file import Canonical, MeltanoFile


definition = {
    # a, b, …, z
    chr(ord("a") + i): i if i % 2 else None
    for i in range(10)
}


class TestCanonical:
    @pytest.fixture
    def subject(self):
        return Canonical(**definition)

    def test_canonical(self, subject):
        # make sure the Nones are removed
        assert len(list(subject)) == 5

        subject.test = "hello"
        yaml_definition = "\n".join(f"{k}: {v}" for k, v in iter(subject))

        assert yaml.dump(subject).strip() == yaml_definition

    def test_false(self, subject):
        subject.false_value = False

        assert subject.canonical()["false_value"] is False

    def test_nested(self, subject):
        nested = Canonical(test="value")
        subject.nested = nested

        assert Canonical.as_canonical(subject)["nested"] == Canonical.as_canonical(
            nested
        )


class TestMeltanoFile:
    def test_load(self, project, tap, target):
        definition = project.meltano

        meltano_file = MeltanoFile.parse(project.meltano)
        assert meltano_file
