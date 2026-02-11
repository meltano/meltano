from __future__ import annotations

import json
import typing as t
from importlib.metadata import distribution


class Pep610DirInfo(t.TypedDict):
    """PEP 610 directory information."""

    editable: bool


class Pep610Data(t.TypedDict):
    """PEP 610 data."""

    url: str
    dir_info: Pep610DirInfo


def _get_pep610_data() -> Pep610Data | None:
    dist = distribution("meltano")
    if contents := dist.read_text("direct_url.json"):
        return json.loads(contents)

    return None


def editable_installation() -> str | None:
    pep610_data = _get_pep610_data()
    if pep610_data is None:
        return None

    if (  # pragma: no branch
        (url := pep610_data.get("url"))
        and (dir_info := pep610_data.get("dir_info", {}))  # type: ignore[redundant-expr]
        and dir_info.get("editable", False)
    ):
        return url.removeprefix("file://")

    return None
