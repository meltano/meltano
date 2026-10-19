# ruff: file-ignore[non-empty-init-module]  # ruff:ignore[undocumented-public-package]

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from meltano.core.plugin import PluginType

    ExitCodes: t.TypeAlias = Mapping[PluginType, int]


class RunnerError(Exception):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        message: str,
        exitcodes: ExitCodes | None = None,
    ) -> None:
        super().__init__(message)
        self.exitcodes: ExitCodes = {} if exitcodes is None else exitcodes


class Runner:  # noqa: D101
    def run(self) -> None:  # noqa: D102
        pass
