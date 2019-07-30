import logging
import humps
from enum import Enum
from collections.abc import Mapping, Iterable
from flask import request, json


class FrozenDict(dict):
    pass


def freeze_keys(d: dict):
    """
    Mark the dictionary as frozen, no automatic conversion
    will be operated on it.
    """
    return FrozenDict(d)


class JSONScheme(str, Enum):
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"


def key_convert(obj, converter):
    if isinstance(obj, dict) and not isinstance(obj, FrozenDict):
        converted = {}
        for k, v in obj.items():
            new_k = converter(k)

            if new_k in converted:
                raise ValueError(f"Naming scheme conversion conflict on `{new_k}`")

            converted[new_k] = key_convert(v, converter)

        return converted
    elif isinstance(obj, list):
        return [key_convert(x, converter) for x in obj]
    else:
        return obj


class JSONSchemeDecoder(json.JSONDecoder):
    """
    This JSONDecoder normalizes the returned `dict` to
    use `snake` case naming scheme.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, object_hook=self.hook)

    def hook(self, obj):
        # transform to snakecase
        obj = key_convert(obj, humps.decamelize)

        return obj


class JSONSchemeEncoder(json.JSONEncoder):
    """
    This JSONEncoder supports the `X-JSON-SCHEME` header to
    send the payload using requested naming scheme.

    Available schemes are `camel` and `snake`.
    Defaults to `snake`.
    """

    case_strategies = {
        JSONScheme.CAMEL_CASE: humps.camelize,
        JSONScheme.SNAKE_CASE: humps.decamelize,
    }

    def encode(self, obj):
        try:
            scheme = request.headers.get("X-Json-Scheme")
            strategy = self.__class__.case_strategies[scheme]
            logging.debug(f"Using JSON Scheme: {scheme}")
            obj = key_convert(obj, strategy)
        except KeyError:
            pass

        return super().encode(obj)


def setup_json(app):
    app.json_encoder = JSONSchemeEncoder
    app.json_decoder = JSONSchemeDecoder

    # flask-restful uses its own encoder
    app.config["RESTFUL_JSON"]["cls"] = app.json_encoder
