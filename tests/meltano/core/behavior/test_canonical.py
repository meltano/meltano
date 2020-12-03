import pytest
import yaml

from meltano.core.behavior.canonical import Canonical

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

    def test_nested_empty(self, subject):
        nested = Canonical(test="")
        subject.nested = nested

        assert "nested" not in Canonical.as_canonical(subject)

    def test_update_canonical(self, subject):
        subject.update(Canonical(test="value"))
        assert subject.test == "value"

    def test_update_dict(self, subject):
        subject.update({"test": "value"})
        assert subject.test == "value"

    def test_update_kwargs(self, subject):
        subject.update(test="value")
        assert subject.test == "value"
