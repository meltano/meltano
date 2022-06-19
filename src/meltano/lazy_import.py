"""Utility to make most imports within the `meltano` package lazy by default.

"Lazy" in this case means as it does in [PEP-0690](https://peps.python.org/pep-0690/):

> [...] transparently defer the execution of imported modules until the moment when an imported
object is used.

Justification follows in the PEP:

> Since Python programs commonly import many more modules than a single invocation of the program
is likely to use in practice, lazy imports can greatly reduce the overall number of modules loaded,
improving startup time and memory usage.

In Meltano's case, having eager imports results in a relatively high startup time that is incurred
every time the CLI is run. This includes when it is run to perform tab-completion, where the delay
is especially noticable.

An exception is made for the `meltano.cli` module, whose import has the side-effect of defining
the Click CLI. It is loaded eagerly.
"""
from __future__ import annotations

import sys
from importlib.machinery import FrozenImporter, ModuleSpec, PathFinder
from importlib.util import LazyLoader
from types import ModuleType
from typing import Sequence


class MeltanoLazyPathFinder(PathFinder):
    """A `PathFinder` subclass that performs lazy imports for Meltano modules."""

    @classmethod
    def find_spec(
        cls,
        fullname: str,
        path: Sequence[bytes | str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Try to find a spec for the Meltano module `fullname` on `sys.path` or `path`.

        If found, the spec's loader will be wrapped with a `LazyLoader`.

        The search is based on `sys.path_hooks` and `sys.path_importer_cache`.

        Parameters:
            fullname: The fully qualified name of the module being searched for.
            path: Module locations to search instead of `sys.path`.
            target: A module object that the finder may use to make a more educated guess about
                what spec to return.

        Returns:
            The spec for a module in the `meltano` package, or `None` if not applicable or found.
        """
        if not fullname.startswith("meltano") or fullname.startswith("meltano.cli"):
            return None
        spec = super().find_spec(fullname, path, target)
        if spec is None:
            return None
        if spec.loader is None:
            return None
        spec.loader = LazyLoader(spec.loader)
        return spec


def install() -> None:
    """Install `MeltanoLazyPathFinder` into `sys.meta_path` after `FrozenImporter`.

    Note that the items in `sys.meta_path` are tried in order during an import until one of them
    returns something other than `None`.

    Raises:
        Exception: Unable to install `MeltanoLazyPathFinder` into `sys.meta_path`.
    """
    try:
        sys.meta_path.insert(sys.meta_path.index(FrozenImporter), MeltanoLazyPathFinder)
    except ValueError as ex:
        raise Exception(
            "Unable to install `MeltanoLazyPathFinder` into `sys.meta_path`"
        ) from ex
