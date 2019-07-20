import pytest
from flask import json
import json as _json


class TestJSON:
    @pytest.mark.parametrize(
        "scheme,expected",
        [
            ("camel", {"snakeCase": {"snakeCase": 1}}),
            ("snake", {"snake_case": {"snake_case": 1}}),
        ],
    )
    def test_json_scheme_encoder(self, app, scheme, expected):
        payload = {"snake_case": {"snake_case": 1}}

        with app.test_request_context(headers={"X-Json-Scheme": scheme}):
            encoded = json.dumps(payload)

            # load with a Vanilla decoder
            decoded = _json.loads(encoded)

            assert decoded == expected

    @pytest.mark.parametrize(
        "payload", [{"snakeCase": {"snakeCase": 1}}, {"snake_case": {"snake_case": 1}}]
    )
    def test_json_scheme_decoder(self, app, payload):
        expected = {"snake_case": {"snake_case": 1}}

        with app.test_request_context():
            encoded = _json.dumps(payload)
            decoded = json.loads(encoded)

            assert decoded == expected

    def test_json_scheme_fails(self, app):
        payload = {"snakeCase": 1, "snake_case": 2}

        with pytest.raises(ValueError) as e, \
          app.test_request_context():
            encoded = _json.dumps(payload)
            json.loads(encoded)
