import uuid
from datetime import datetime

from meltano.core.sqlalchemy import GUID
from . import db


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    recipient = db.Column(db.String(), nullable=False)
    event_type = db.Column(db.String(), nullable=False)
    source_type = db.Column(db.String(), nullable=True)
    source_id = db.Column(db.String(), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
