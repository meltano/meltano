import stringcase
from flask import request, json
from enum import Enum


class JSONScheme(str, Enum):
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"


def key_convert(obj, converter):
    if not isinstance(obj, dict):
        return obj

    converted = {}
    for k, v in obj.items():
        new_k = converter(k)

        if new_k in converted:
            raise ValueError(f"Naming scheme conversion conflict on `{new_k}`")

        if isinstance(v, dict):
            converted[new_k] = key_convert(v, converter)
        else:
            converted[new_k] = v

    return converted


class JSONSchemeDecoder(json.JSONDecoder):
    """
    This JSONDecoder normalizes the returned `dict` to
    use `snake` case naming scheme.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, object_hook=self.hook)

    def hook(self, obj):
        # transform to snakecase
        obj = key_convert(obj, stringcase.snakecase)

        return obj


class JSONSchemeEncoder(json.JSONEncoder):
    """
    This JSONEncoder supports the `X-JSON-SCHEME` header to
    send the payload using requested naming scheme.

    Available schemes are `camel` and `snake`.
    Defaults to `snake`.
    """

    case_strategies = {
        JSONScheme.CAMEL_CASE: stringcase.camelcase,
        JSONScheme.SNAKE_CASE: stringcase.snakecase,
    }

    def encode(self, obj):
        scheme = request.headers.get("X-Json-Scheme", JSONScheme.SNAKE_CASE)
        strategy = self.__class__.case_strategies[scheme]
        obj = key_convert(obj, strategy)

        return super().encode(obj)


def setup_json(app):
    app.json_encoder = JSONSchemeEncoder
    app.json_decoder = JSONSchemeDecoder

    # flask-restful uses its own encoder
    app.config["RESTFUL_JSON"]["cls"] = app.json_encoder
