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

    def test_with_attrs(self, subject):
        subject.test = "value"

        assert subject.with_attrs().canonical() == subject.canonical()

        new = subject.with_attrs(test="other_value")
        assert new.test == "other_value"
        assert new.canonical() == {**subject.canonical(), "test": "other_value"}

        new = subject.with_attrs(new_test="new_value")
        assert new.new_test == "new_value"
        assert new.canonical() == {**subject.canonical(), "new_test": "new_value"}

    def test_defaults(self, subject):
        with pytest.raises(AttributeError):
            subject.test

        subject.test = None

        assert subject.test is None

        # This would typically be set from a Canonical subclass
        subject._defaults["test"] = lambda _: "default"

        # Default values show up when getting an attr
        assert subject.test == "default"
        # But they're not included in the canonical representation
        assert "test" not in subject.canonical()

        subject.test = "changed"

        assert subject.test == "changed"
        assert subject.canonical()["test"] == "changed"

    def test_fallbacks(self, subject):
        # Calling an unknown attribute is not supported
        with pytest.raises(AttributeError):
            subject.unknown

        fallback = Canonical(unknown="value", known="value")
        # This would typically be set from a Canonical subclass
        subject._fallback_to = fallback

        # Unknown attributes fall back
        assert subject.unknown == "value"
        assert "unknown" not in subject.canonical()

        # Known attributes don't fall back
        subject.known = None
        assert subject.known is None

        # Unless we make them
        subject._fallbacks.add("known")
        assert subject.known == "value"
        assert "known" not in subject.canonical()

        # Unless there is nothing to fallback to
        subject._fallback_to = None
        assert subject.known is None

        # Defaults are still applied
        subject._defaults["known"] = lambda _: "default"
        assert subject.known == "default"
        assert "known" not in subject.canonical()

        # Until a value is set
        subject.known = "value"
        assert subject.known == "value"
        assert subject.canonical()["known"] == "value"
