from __future__ import annotations

import inspect
import json
import platform
import typing as t
import uuid
import warnings
from pathlib import Path
from platform import python_version_tuple

import pytest
from jsonschema import ValidationError, validate

from meltano.core import tracking
from meltano.core.tracking.contexts import ExceptionContext
from meltano.core.utils import hash_sha256
from meltano.core.utils.compat import importlib_resources

THIS_FILE_BASENAME = Path(__file__).name

with (
    importlib_resources.files(tracking)
    / "iglu-client-embedded"
    / "schemas"
    / "com.meltano"
    / "exception_context"
    / "jsonschema"
    / "1-0-0"
).open() as exception_context_schema_file:
    EXCEPTION_CONTEXT_SCHEMA = json.load(exception_context_schema_file)


class CustomException(Exception):
    """A custom exception type to be used in `test_complex_exception_context`."""


def is_valid_exception_context(instance: dict[str, t.Any]) -> bool:
    try:
        with warnings.catch_warnings():
            # Ignore the misleading warning thrown by `jsonschema`:
            #     The metaschema specified by `$schema` was not found. Using
            #     the latest draft to validate, but this will raise an error
            #     in the future.
            # This is a bug in `jsonschema`, as our value for `$schema` is fine.
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            validate(instance, EXCEPTION_CONTEXT_SCHEMA)
    except ValidationError:
        return False
    return True


def test_null_exception_context() -> None:
    ctx = ExceptionContext()
    assert isinstance(ctx.data, dict)
    assert isinstance(ctx.data["context_uuid"], str)
    uuid.UUID(ctx.data["context_uuid"], version=4)
    assert ctx.data["exception"] is None


def test_simple_exception_context() -> None:
    msg = "The error message"

    ex = ValueError(msg)
    try:
        raise ex
    except Exception:
        ctx = ExceptionContext()

    assert is_valid_exception_context(ctx.data)

    ex_data = ctx.data["exception"]

    assert ex_data["type"] == "ValueError"
    assert (
        ex_data["str_hash"]
        == "84e45725cb2d98b23d365ff46d8aae35a23c6d91fbed6c0b19ad2ddb72e66f01"
        == hash_sha256(str(ex))
        == hash_sha256(msg)
    )
    assert (
        ex_data["repr_hash"]
        == "544806225e70d8ae22a4826a02b0be4320a71c1d3b5f0aa4630828815bee76b1"
        == hash_sha256(repr(ex))
        == hash_sha256(f"ValueError({msg!r})")
    )

    assert ex_data["cause"] is None
    assert ex_data["context"] is None

    tb_data = ex_data["traceback"]
    assert len(tb_data) == 1
    for key in ("file", "line_number"):
        assert key in tb_data[0]


def test_complex_exception_context() -> None:
    if platform.system() == "Windows":
        pytest.xfail("Fails on Windows: https://github.com/meltano/meltano/issues/3444")

    line_nums: list[int] = []
    file_not_found_error = None

    def _function_to_deepen_traceback() -> None:
        try:
            line_nums.append(1 + inspect.currentframe().f_lineno)
            Path("/tmp/fake/path/will/not/resolve").resolve(strict=True)  # noqa: S108
        except Exception as ex:
            nonlocal file_not_found_error
            file_not_found_error = ex
            line_nums.append(1 + inspect.currentframe().f_lineno)
            raise ValueError("that path was a bad value") from ex  # noqa: EM101

    try:
        try:
            line_nums.append(1 + inspect.currentframe().f_lineno)
            _function_to_deepen_traceback()
        except Exception:
            line_nums.append(1 + inspect.currentframe().f_lineno)
            raise CustomException from None
    except Exception:
        ctx = ExceptionContext()

    assert is_valid_exception_context(ctx.data)

    major, minor, _ = python_version_tuple()

    cause = ctx.data["exception"]["context"].pop("cause")
    context = ctx.data["exception"]["context"].pop("context")

    assert cause == context
    assert cause["type"] == "FileNotFoundError"
    assert cause["str_hash"] == hash_sha256(str(file_not_found_error))
    assert cause["repr_hash"] == hash_sha256(repr(file_not_found_error))
    assert cause["traceback"][0] == {
        "file": f".../{THIS_FILE_BASENAME}",
        "line_number": line_nums[1],
    }
    assert cause["traceback"][1]["file"] == f"lib/python{major}.{minor}/pathlib.py"
    assert cause["cause"] is None
    assert cause["context"] is None

    assert ctx.data == {
        "context_uuid": ctx.data["context_uuid"],
        "exception": {
            "type": "CustomException",
            "str_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # noqa: E501
            "repr_hash": "ad9443d77d731da456747bd47282a51afe86be7058533f44dcc979320ad62c73",  # noqa: E501
            "traceback": [
                {
                    "file": f".../{THIS_FILE_BASENAME}",
                    "line_number": line_nums[3],
                },
            ],
            "cause": None,
            "context": {
                "type": "ValueError",
                "str_hash": "1009263b7f48917b8f0edafcfc8a06d22156122fbcbfbb7c9139f420b8472e0c",  # noqa: E501
                "repr_hash": "0015450e35aed13f4802973752ee45d02c8f8eaa5d57417962986f4b8ef1bf88",  # noqa: E501
                "traceback": [
                    {
                        "file": f".../{THIS_FILE_BASENAME}",
                        "line_number": line_nums[0],
                    },
                    {
                        "file": f".../{THIS_FILE_BASENAME}",
                        "line_number": line_nums[2],
                    },
                ],
            },
        },
    }
