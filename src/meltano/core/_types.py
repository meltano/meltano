from __future__ import annotations

import os
import sys
import typing as t

if sys.version_info < (3, 10):
    from typing import TypeAlias  # noqa: ICN003
else:
    from typing_extensions import TypeAlias

StrPath: TypeAlias = t.Union[str, os.PathLike[str]]
