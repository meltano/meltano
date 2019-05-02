import pytest

from meltano.core.utils import nest


def test_nest():
    subject = {}

    b = nest(subject, "a.b")
    b["val"] = 1
    assert b == {"val": 1}

    c = nest(subject, "a.b.c")
    c["val"] = 2
    assert b == {"val": 1, "c": {"val": 2}}

    arr = nest(subject, "a.list", value=[])

    VALUE = {"value": 1}
    val = nest(subject, "a.value", value=VALUE)

    assert subject["a"]["b"] is b
    assert subject["a"]["b"]["c"] is c
    assert isinstance(arr, list)
    # make sure it is a copy
    assert val == VALUE and not val is VALUE
