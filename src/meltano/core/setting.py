from __future__ import annotations  # noqa: D100

import sys
import typing as t

from sqlalchemy import types
from sqlalchemy.orm import Mapped, mapped_column

from meltano.core.sqlalchemy import StrPK  # noqa: TC001

from .models import SystemModel

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override


class Setting(SystemModel):  # noqa: D101
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    label: Mapped[t.Optional[str]]  # noqa: UP045
    description: Mapped[t.Optional[str]] = mapped_column(types.Text)  # noqa: UP045

    # represent a materialized path to support
    # a nested configuration.
    name: Mapped[StrPK]
    namespace: Mapped[t.Optional[StrPK]]  # noqa: RUF100, UP007, UP045
    value: Mapped[t.Optional[str]] = mapped_column(types.PickleType)  # noqa: UP045
    enabled: Mapped[bool] = mapped_column(default=False)

    @override
    def __repr__(self) -> str:
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.namespace}) {self.name}={self.value} {enabled_marker}>"
