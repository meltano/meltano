from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import validates

from meltano.core import utils
from meltano.core.sqlalchemy import GUID

from . import db


class SubscriptionEventType(str, Enum):
    PIPELINE_MANUAL_RUN = "pipeline_manual_run"


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    recipient = db.Column(db.String(), nullable=False)
    event_type = db.Column(db.String(), nullable=False)
    source_type = db.Column(db.String(), nullable=True)
    source_id = db.Column(db.String(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    @validates("recipient")
    def validate_recipient(self, key, recipient):
        if not utils.is_email_valid(recipient):
            raise AssertionError(
                f"Validation failed: `{key}` must be a valid email address."
            )

        return recipient
