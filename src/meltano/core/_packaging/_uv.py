from __future__ import annotations

from functools import cache


@cache
def find_uv() -> str:
    """Find the `uv` executable.

    Tries to import the `uv` package and use its `find_uv_bin` function to find the
    `uv` executable. If that fails, falls back to using the `uv` executable on the
    system PATH. If it can't be found on the PATH, returns `"uv"`.

    Adapted from https://github.com/wntrblm/nox/blob/55c7eaf2eb03feb4a4b79e74966c542b75d61401/nox/virtualenv.py#L42-L54.

    Copyright 2016 Alethea Katherine Flowers

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Returns:
        A string representing the path to the `uv` executable.

    Raises:
        MeltanoError: The `uv` executable could not be found.
    """
    from uv import find_uv_bin

    return find_uv_bin()
