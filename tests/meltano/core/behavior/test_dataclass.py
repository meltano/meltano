from __future__ import annotations

import io
from dataclasses import dataclass, field
from textwrap import dedent

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from meltano.core.behavior._dataclass import (
    CanonicalDataclassMeta,
    CanonicalDataclassMixin,
)


@dataclass(eq=False)
class _Nested(CanonicalDataclassMixin, metaclass=CanonicalDataclassMeta):
    value: str | None = None


@dataclass(eq=False)
class _Subject(CanonicalDataclassMixin, metaclass=CanonicalDataclassMeta):
    name: str = "test"
    optional: str | None = None
    flag: bool = False
    items: list[str] = field(default_factory=list)
    mapping: dict[str, str] = field(default_factory=dict)
    nested: _Nested | None = None


class TestCanonicalDataclassMixin:
    def test_none_and_empty_values_excluded(self) -> None:
        subject = _Subject(name="hello")
        assert subject.canonical() == {"name": "hello", "flag": False}

    def test_false_value_included(self) -> None:
        subject = _Subject(name="hello", flag=True)
        assert subject.canonical()["flag"] is True

    def test_list_values_canonicalized(self) -> None:
        subject = _Subject(name="hello", items=["a", "b"])
        assert subject.canonical()["items"] == ["a", "b"]

    def test_dict_values_canonicalized(self) -> None:
        subject = _Subject(name="hello", mapping={"a": "1"})
        assert subject.canonical()["mapping"] == {"a": "1"}

    def test_commented_map_values_preserve_comments(self) -> None:
        contents = dedent(
            """\
            name: hello
            mapping:
              # comment on a mapping entry
              a: '1'
            """,
        )
        yaml = YAML()
        parsed_mapping = yaml.load(io.StringIO(contents))
        subject = _Subject.parse(parsed_mapping)
        assert subject is not None

        out = io.StringIO()
        yaml.dump(subject.canonical(), out)
        assert out.getvalue() == dedent(
            """\
            name: hello
            flag: false
            mapping:
              # comment on a mapping entry
              a: '1'
            """,
        )

    def test_set_values_canonicalized(self) -> None:
        # `_canonize` is exercised directly since dataclass fields are typed,
        # but the underlying `as_canonical` also supports arbitrary sets.
        assert sorted(_Subject.as_canonical({"a", "b"})) == ["a", "b"]

    def test_nested_dataclass_included(self) -> None:
        subject = _Subject(name="hello", nested=_Nested(value="x"))
        assert subject.canonical()["nested"] == {"value": "x"}

    def test_nested_empty_dataclass_excluded(self) -> None:
        subject = _Subject(name="hello", nested=_Nested())
        assert "nested" not in subject.canonical()

    def test_extra_kwargs_stored(self) -> None:
        subject = _Subject(name="hello", unknown="value")
        assert subject._extra_attrs == {"unknown": "value"}
        assert subject._dict["unknown"] == "value"

    def test_getitem_setitem(self) -> None:
        subject = _Subject(name="hello")
        assert subject["name"] == "hello"
        subject["name"] = "changed"
        assert subject.name == "changed"

    def test_attrs_property(self) -> None:
        subject = _Subject(name="hello")
        assert subject.attrs is subject._dict

    def test_parse_returns_instance_as_is(self) -> None:
        subject = _Subject(name="hello")
        assert _Subject.parse(subject) is subject

    def test_parse_none(self) -> None:
        assert _Subject.parse(None) is None

    def test_parse_dict_filters_unknown_fields(self) -> None:
        parsed = _Subject.parse({"name": "hello", "unknown": "ignored"})
        assert parsed is not None
        assert parsed.name == "hello"
        assert "unknown" not in parsed._extra_attrs

    def test_parse_preserves_comments(self) -> None:
        contents = dedent(
            """\
            # top-level comment
            name: hello
            items:
            # comment in list
            - a # trailing comment
            """,
        )
        yaml = YAML()
        mapping = yaml.load(io.StringIO(contents))
        subject = _Subject.parse(mapping)
        assert subject is not None
        assert subject.name == "hello"
        assert subject.items[0] == "a"

        out = io.StringIO()
        yaml.dump(subject.canonical(), out)
        assert out.getvalue() == dedent(
            """\
            # top-level comment
            name: hello
            flag: false
            items:
            # comment in list
            - a # trailing comment
            """,
        )

    def test_annotations_round_trip(self) -> None:
        original = CommentedMap(
            {"name": "hello", "annotations": {"cloud": {"data": 1}}},
        )
        subject = _Subject.parse(original)
        assert subject is not None
        assert subject.name == "hello"
        canonical = dict(subject.canonical())
        assert canonical["annotations"] == original["annotations"]
        assert canonical["flag"] is False

    def test_yaml_classmethod(self) -> None:
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.representer.add_representer(_Subject, _Subject.yaml)

        buf = io.StringIO()
        yaml.dump(_Subject(name="hello"), buf)
        assert buf.getvalue() == "name: hello\nflag: false\n"

    def test_to_yaml_classmethod(self) -> None:
        yaml = YAML(typ="safe")
        yaml.representer.add_representer(_Subject, _Subject.to_yaml)

        buf = io.StringIO()
        yaml.dump(_Subject(name="hello"), buf)
        assert buf.getvalue() == "{flag: false, name: hello}\n"
