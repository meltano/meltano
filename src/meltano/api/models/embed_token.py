from datetime import datetime
from enum import Enum
from secrets import token_urlsafe

from . import db


TOKEN_BITS_SIZE = 32


class ResourceType(str, Enum):
    REPORT = "report"
    DASHBOARD = "dashboard"


def generate_token(cls):
    return token_urlsafe(TOKEN_BITS_SIZE)


class EmbedToken(db.Model):
    __tablename__ = "embed_tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(), default=generate_token, unique=True)
    resource_id = db.Column(db.String(), nullable=False)
    resource_type = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
