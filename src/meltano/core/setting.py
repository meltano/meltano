from __future__ import annotations

from sqlalchemy import Column, types
from sqlalchemy.orm import Mapped

from .models import SystemModel


class Setting(SystemModel):
    __tablename__ = "plugin_settings"

    # represent the mapping to the ENV
    label: Mapped[str] = Column(types.String)
    description: Mapped[str] = Column(types.Text)

    # represent a materialized path to support
    # a nested configuration.
    name: Mapped[str] = Column(types.String, primary_key=True)
    namespace: Mapped[str] = Column(types.String, primary_key=True, nullable=True)
    value: Mapped[str] = Column(types.PickleType)
    enabled: Mapped[bool] = Column(types.Boolean, default=False)

    def __repr__(self):
        enabled_marker = "E" if self.enabled else ""
        return f"<({self.namespace}) {self.name}={self.value} {enabled_marker}>"
