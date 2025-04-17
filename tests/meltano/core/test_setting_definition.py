from __future__ import annotations

import re

import pytest

from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.utils import REGEX_ISO8601, parse_date


class TestSettingDefinition:
    @pytest.mark.parametrize(
        ("setting_definition", "uncast_expected_pairs"),
        (
            (
                SettingDefinition(name="test_setting", kind=SettingKind.ARRAY),
                (
                    ('["abc", "xyz"]', ["abc", "xyz"]),
                    ('["abc", "xyz",]', ["abc", "xyz"]),
                    ("['abc', 'xyz']", ["abc", "xyz"]),
                    ("[abc, xyz]", ValueError),
                    ("'abc', 'xyz'", ["abc", "xyz"]),
                    ("'abc', 'xyz',", ["abc", "xyz"]),
                    ('[null, "xyz"]', [None, "xyz"]),
                    ("{'abc', 'xyz'}", ValueError),
                    ("1234", ValueError),
                    ("[1234, 5678]", [1234, 5678]),
                ),
            ),
            (
                SettingDefinition(name="test_setting", kind=SettingKind.OBJECT),
                (
                    (
                        '{"key_1": "value_1", "key_2": "value_2"}',
                        {"key_1": "value_1", "key_2": "value_2"},
                    ),
                    ('{"key": "value",}', {"key": "value"}),
                    ('{"key": null}', {"key": None}),
                    ("{'key': null}", ValueError),
                    ("key: value", ValueError),
                    ("{'key': 'value'}", {"key": "value"}),
                    ("{key: value}", ValueError),
                    ("{'abc', 'xyz'}", ValueError),
                    ("1234", ValueError),
                ),
            ),
        ),
        ids=("array", "object"),
    )
    def test_cast_value_array(
        self,
        setting_definition: SettingDefinition,
        uncast_expected_pairs,
    ) -> None:
        for uncast, expected in uncast_expected_pairs:
            if isinstance(expected, type) and issubclass(expected, Exception):
                with pytest.raises(expected):
                    setting_definition.cast_value(uncast)
            else:
                assert setting_definition.cast_value(uncast) == expected

    def test_cast_options(self) -> None:
        setting_definition = SettingDefinition(
            name="test_setting",
            kind=SettingKind.OPTIONS,
            options=[
                {"value": "abc", "label": "ABC"},
                {"value": "xyz", "label": "XYZ"},
            ],
        )

        assert setting_definition.cast_value("abc") == "abc"
        assert setting_definition.cast_value("xyz") == "xyz"
        assert setting_definition.cast_value(None) is None
        with pytest.raises(ValueError, match="is not a valid choice"):
            setting_definition.cast_value("def")

    @pytest.mark.parametrize(
        ("setting_definition"),
        (
            pytest.param(
                SettingDefinition(name="test_setting", kind=SettingKind.DATE_ISO8601),
                id="date_iso8601",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    kind=SettingKind.STRING,
                    value_post_processor="parse_date",
                ),
                id="string_parse_date",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    kind=SettingKind.STRING,
                    value_post_processor=parse_date,
                ),
                id="string_parse_date_callable",
            ),
        ),
    )
    def test_post_process_parse_date(
        self,
        setting_definition: SettingDefinition,
    ) -> None:
        post_process = setting_definition.post_process_value
        assert post_process(None) is None
        assert post_process("not a date") == "not a date"

        datetime_with_offset = "2021-01-01T00:00:00+00:00"
        assert post_process(datetime_with_offset) == datetime_with_offset

        datetime_with_z = "2021-01-01T00:00:00Z"
        assert post_process(datetime_with_z) == datetime_with_z

        datetime_with_space = "2021-01-01 00:00:00"
        assert post_process(datetime_with_space) == datetime_with_space

        date_only = "2021-01-01"
        assert post_process(date_only) == date_only

        assert re.match(REGEX_ISO8601, post_process("3 days ago, UTC"))

    @pytest.mark.parametrize(
        ("setting_definition", "sensitive", "kind"),
        (
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=True,
                    kind=SettingKind.STRING,
                ),
                True,
                SettingKind.STRING,
                id="sensitive-string",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=True,
                    kind=SettingKind.PASSWORD,
                ),
                True,
                SettingKind.STRING,
                id="sensitive-password",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=False,
                    kind=None,
                ),
                False,
                None,
                id="sensitive-no-kind",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=False,
                    kind=SettingKind.STRING,
                ),
                False,
                SettingKind.STRING,
                id="non-sensitive-string",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=False,
                    kind=SettingKind.PASSWORD,
                ),
                True,
                SettingKind.PASSWORD,
                id="non-sensitive-password",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=False,
                    kind=None,
                ),
                False,
                None,
                id="non-sensitive-no-kind",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=None,
                    kind=SettingKind.STRING,
                ),
                None,
                SettingKind.STRING,
                id="no-sensitive-string",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=None,
                    kind=SettingKind.PASSWORD,
                ),
                True,
                SettingKind.PASSWORD,
                id="no-sensitive-password",
            ),
            pytest.param(
                SettingDefinition(
                    name="test_setting",
                    sensitive=None,
                    kind=None,
                ),
                None,
                None,
                id="no-sensitive-no-kind",
            ),
        ),
    )
    def test_parse(
        self,
        setting_definition: SettingDefinition,
        *,
        sensitive: bool,
        kind: SettingKind,
    ) -> None:
        assert setting_definition.sensitive is sensitive
        assert setting_definition.kind is kind

    def test_parse_missing_name(self) -> None:
        with pytest.raises(
            TypeError,
            match="missing 1 required keyword-only argument: 'name'",
        ):
            SettingDefinition()
