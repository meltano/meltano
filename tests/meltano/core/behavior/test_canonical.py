from __future__ import annotations

import io
from textwrap import dedent

import pytest
from ruamel.yaml.comments import CommentedMap

from meltano.core.behavior.canonical import Canonical
from meltano.core.yaml import yaml

definition = {
    # {'a': None, 'b': 1, 'c': None, 'd': 3, 'e': None, ...}
    chr(ord("a") + i): i if i % 2 else None
    for i in range(10)
}


class TestCanonical:
    @pytest.fixture
    def subject(self):
        return Canonical(**definition)

    def test_canonical(self, subject) -> None:
        # make sure the Nones are removed
        assert len(list(subject)) == 5

        subject.test = "hello"
        yaml_definition = "\n".join(f"{k}: {v}" for k, v in iter(subject))

        buf = io.StringIO()
        yaml.dump(subject, buf)
        buf.seek(0)

        assert buf.read().strip() == yaml_definition

    def test_false(self, subject) -> None:
        subject.false_value = False

        assert subject.canonical()["false_value"] is False

    def test_nested(self, subject) -> None:
        nested = Canonical(test="value")
        subject.nested = nested

        assert Canonical.as_canonical(subject)["nested"] == Canonical.as_canonical(
            nested,
        )

    def test_nested_empty(self, subject) -> None:
        nested = Canonical(test="")
        subject.nested = nested

        assert "nested" not in Canonical.as_canonical(subject)

    def test_update_canonical(self, subject) -> None:
        subject.update(Canonical(test="value"))
        assert subject.test == "value"

    def test_update_dict(self, subject) -> None:
        subject.update({"test": "value"})
        assert subject.test == "value"

    def test_update_kwargs(self, subject) -> None:
        subject.update(test="value")
        assert subject.test == "value"

    def test_with_attrs(self, subject) -> None:
        subject.test = "value"

        assert subject.with_attrs().canonical() == subject.canonical()

        new = subject.with_attrs(test="other_value")
        assert new.test == "other_value"
        assert new.canonical() == {**subject.canonical(), "test": "other_value"}

        new = subject.with_attrs(new_test="new_value")
        assert new.new_test == "new_value"
        assert new.canonical() == {**subject.canonical(), "new_test": "new_value"}

    def test_defaults(self, subject) -> None:
        with pytest.raises(AttributeError):
            subject.test  # noqa: B018

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

    def test_fallbacks(self, subject) -> None:
        # Calling an unknown attribute is not supported
        with pytest.raises(AttributeError):
            subject.unknown  # noqa: B018

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

    def test_preserve_comments(self) -> None:
        contents = """\
            # This is a top-level comment
            test: value

            object:
              # Comment in an object
              key: value # Comment in a nested value

            array:
            # Comment in an array
            - value # Comment in an array element
        """
        contents = dedent(contents)
        mapping = yaml.load(io.StringIO(contents))
        subject = Canonical.parse(mapping)
        assert subject.test == "value"
        assert subject.object["key"] == "value"
        assert subject.array[0] == "value"

        obj = subject.canonical()
        assert isinstance(obj, CommentedMap)

        out_stream = io.StringIO()
        yaml.dump(obj, out_stream)
        out_stream.seek(0)
        new_contents = out_stream.read()
        assert new_contents == contents

    def test_annotations(self) -> None:
        original = CommentedMap(
            {"a": 1, "annotations": {"cloud": {"data": 123}}, "z": -1},
        )
        obj = Canonical.parse(original)
        assert obj.a == 1
        with pytest.raises(AttributeError):
            assert obj.annotations
        assert obj.z == -1
        assert obj.canonical() == original
