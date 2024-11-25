from __future__ import annotations  # noqa: D100

import typing as t

from sqlalchemy import types
from sqlalchemy.orm import Mapped, mapped_column

from meltano.core.sqlalchemy import StrPK  # noqa: TC001

from .models import SystemModel


class Setting(SystemModel):  # noqa: D101
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    label: Mapped[t.Optional[str]]  # noqa: UP007
    description: Mapped[t.Optional[str]] = mapped_column(types.Text)  # noqa: UP007

    # represent a materialized path to support
    # a nested configuration.
    name: Mapped[StrPK]
    namespace: Mapped[t.Optional[StrPK]]  # noqa: UP007
    value: Mapped[t.Optional[str]] = mapped_column(types.PickleType)  # noqa: UP007
    enabled: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:  # noqa: D105
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.namespace}) {self.name}={self.value} {enabled_marker}>"
