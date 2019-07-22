import pytest
from flask import json
import json as _json


class TestJSON:
    @pytest.mark.parametrize(
        "scheme,expected",
        [
            (
                "camel",
                {
                    "aDict": {"snakeCase": 1},
                    "aList": [{"snakeCase": 1}],
                    "aVal": "simple_value",
                },
            ),
            (
                "snake",
                {
                    "a_dict": {"snake_case": 1},
                    "a_list": [{"snake_case": 1}],
                    "a_val": "simple_value",
                },
            ),
        ],
    )
    def test_json_scheme_encoder(self, app, scheme, expected):
        payload = {
            "a_dict": {"snake_case": 1},
            "a_list": [{"snake_case": 1}],
            "a_val": "simple_value",
        }

        with app.test_request_context(headers={"X-Json-Scheme": scheme}):
            encoded = json.dumps(payload)

            # load with a Vanilla decoder
            decoded = _json.loads(encoded)

            assert decoded == expected

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "aDict": {"camelCase": 1},
                "aList": [{"camelCase": 1}],
                "aVal": "simpleValue",
            }
        ],
    )
    def test_json_scheme_decoder(self, app, payload):
        expected = {
            "a_dict": {"camel_case": 1},
            "a_list": [{"camel_case": 1}],
            "a_val": "simpleValue",
        }

        with app.test_request_context():
            encoded = _json.dumps(payload)
            decoded = json.loads(encoded)

            assert decoded == expected

    def test_json_scheme_fails(self, app):
        payload = {"snakeCase": 1, "snake_case": 2}

        with pytest.raises(ValueError) as e, app.test_request_context():
            encoded = _json.dumps(payload)
            json.loads(encoded)
