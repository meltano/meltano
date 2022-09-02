"""Defines JobState model class."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, func, types
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from meltano.core.models import SystemModel
from meltano.core.sqlalchemy import GUID, JSONEncodedDict


class JobState(SystemModel):
    """Model class that represents the current state of a given job.

    Modified during `meltano elt` or `meltano run` runs whenever a
    STATE message is emitted by a Singer target. Also written and read
    by `meltano state` CLI invocations. Only holds the _current_ state
    for a given job_name. Full job run history is held by the Job model.
    """

    __tablename__ = "state"

    id = Column(types.Integer, primary_key=True)

    updated_at = Column(
        types.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    job_name = Column(types.String, unique=True)
    partial_state = Column(MutableDict.as_mutable(JSONEncodedDict))
    completed_state = Column(MutableDict.as_mutable(JSONEncodedDict))
    job_runs = relationship("Job", back_populates="job_state")
