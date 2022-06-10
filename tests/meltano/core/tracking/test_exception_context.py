import uuid

from meltano.core.tracking import ExceptionContext
from meltano.core.utils import hash_sha256


def test_null_exception_context():
    ctx = ExceptionContext()
    assert isinstance(ctx.data, dict)
    assert isinstance(ctx.data["context_uuid"], str)
    uuid.UUID(ctx.data["context_uuid"], version=4)
    assert ctx.data["exception"] is None


def test_simple_exception_context():
    msg = "The error message"

    ex = ValueError(msg)
    try:
        raise ex
    except Exception:
        ctx = ExceptionContext()

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
    for key in ("path", "path_hash", "line_number"):
        assert key in tb_data[0]

    assert len(tb_data[0]['path_hash']) == 64
    assert not set(tb_data[0]['path_hash']) - set('abcdefABCDEF0123456789')


def test_complex_exception_context():
    pass  # TODO
