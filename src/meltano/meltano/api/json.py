from __future__ import annotations

import logging
from enum import Enum

import humps
from flask import current_app, json, request

from meltano.core.utils import compose


class KeyFrozenDict(dict):
    """Dict subclass that marks the dict as "frozen"."""


def freeze_keys(d: dict):
    """Mark the dictionary as frozen - no automatic conversion will be operated on it."""
    if isinstance(d, KeyFrozenDict):
        return d

    return KeyFrozenDict(d)


class JSONScheme(str, Enum):
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"


def key_convert(obj, converter):
    if isinstance(obj, dict) and not isinstance(obj, KeyFrozenDict):
        converted = {}
        for k, v in obj.items():
            # humps fails to convert undescored values
            # see https://github.com/nficano/humps/issues/2
            if k.startswith("_"):
                new_k = k
            else:
                new_k = converter(k)

            if new_k in converted:
                raise ValueError(f"Naming scheme conversion conflict on `{new_k}`")

            converted[new_k] = key_convert(v, converter)

        return converted
    elif isinstance(obj, list):
        return [key_convert(x, converter) for x in obj]
    return obj


class JSONSchemeDecoder(json.JSONDecoder):
    """This JSONDecoder normalizes the returned `dict` to use `snake` case naming scheme."""

    def __init__(self, *args, **kwargs):
        hooks = compose(kwargs.pop("object_hook", None), self.hook)

        super().__init__(*args, **kwargs, object_hook=hooks)

    def hook(self, obj):
        # transform to snakecase if possible
        try:
            return key_convert(obj, humps.decamelize)
        except ValueError as err:
            logging.err(str(err))
            return super().hook(obj)


class JSONSchemeEncoder(json.JSONEncoder):
    """This JSONEncoder supports the `X-JSON-SCHEME` header to send the payload using requested naming scheme.

    Available schemes are `camel` and `snake`.
    Defaults to `snake`.
    """

    case_strategies = {
        JSONScheme.CAMEL_CASE: humps.camelize,
        JSONScheme.SNAKE_CASE: humps.decamelize,
    }

    def encode(self, obj):
        header = current_app.config["JSON_SCHEME_HEADER"]

        try:
            scheme = request.headers.get(header)
            strategy = self.__class__.case_strategies[scheme]
            logging.debug(f"Using JSON Scheme: {scheme}")
            obj = key_convert(obj, strategy)
        except ValueError as err:
            logging.error(str(err))
            # if we can't convert the keys, let's fallback to
            # the default implementation
            return super().encode(obj)
        except KeyError:
            pass

        return super().encode(obj)


def setup_json(app):
    app.json_encoder = JSONSchemeEncoder
    app.json_decoder = JSONSchemeDecoder

    # flask-restful uses its own encoder
    app.config["RESTFUL_JSON"]["cls"] = app.json_encoder
