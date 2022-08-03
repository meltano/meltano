from __future__ import annotations

import json as _json

import pytest
from flask import json


class TestJSON:
    @pytest.mark.parametrize(
        "scheme,payload,expected",
        [
            (
                "camel",
                {
                    "a_dict": {"camel_case": 1},
                    "a_list": [{"camel_case": 1}],
                    "a_val": "camel_value",
                    "_a_val": "camel_value",
                },
                {
                    "aDict": {"camelCase": 1},
                    "aList": [{"camelCase": 1}],
                    "aVal": "camel_value",
                    "_a_val": "camel_value",
                },
            ),
            (
                "snake",
                {
                    "aDict": {"snakeCase": 1},
                    "aList": [{"snakeCase": 1}],
                    "aVal": "snakeValue",
                    "_aVal": "snakeValue",
                },
                {
                    "a_dict": {"snake_case": 1},
                    "a_list": [{"snake_case": 1}],
                    "a_val": "snakeValue",
                    "_aVal": "snakeValue",
                },
            ),
            (
                None,
                {
                    "aDict": {"none_case": 1},
                    "a_list": [{"none_case": 1}],
                    "a_val-test": "none_value",
                },
                {
                    "aDict": {"none_case": 1},
                    "a_list": [{"none_case": 1}],
                    "a_val-test": "none_value",
                },
            ),
        ],
    )
    def test_json_scheme_encoder(self, app, scheme, payload, expected):
        with app.test_request_context(
            headers={app.config["JSON_SCHEME_HEADER"]: scheme}
        ):
            encoded = json.dumps(payload)

            # load with a Vanilla decoder
            decoded = _json.loads(encoded)

            assert decoded == expected

    @pytest.mark.parametrize(
        "payload,expected",
        [
            (
                {
                    "aDict": {"camelCase": 1},
                    "aList": [{"camelCase": 1}],
                    "aVal": "simpleValue",
                    # `_` prefixed are not converted
                    "_aVal": "simpleValue",
                },
                {
                    "a_dict": {"camel_case": 1},
                    "a_list": [{"camel_case": 1}],
                    "a_val": "simpleValue",
                    # `_` prefixed are not converted
                    "_aVal": "simpleValue",
                },
            )
        ],
    )
    def test_json_scheme_decoder(self, app, payload, expected):
        with app.test_request_context():
            encoded = _json.dumps(payload)
            decoded = json.loads(encoded)

            assert decoded == expected

    def test_json_scheme_encoder_fails(self, app):
        payload = {"snakeCase": 1, "snake_case": 2}

        with app.test_request_context():
            encoded = _json.dumps(payload)

            # if there is an issue with the encoding
            # it fallbacks to the original notation
            assert _json.loads(encoded) == payload
