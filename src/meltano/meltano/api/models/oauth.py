from __future__ import annotations

from datetime import datetime

from . import db

DEFAULT_VARCHAR_LENGTH = 255


class OAuth(db.Model):
    __tablename__ = "oauth"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    provider_id = db.Column(db.String(DEFAULT_VARCHAR_LENGTH))
    provider_user_id = db.Column(db.Integer)
    access_token = db.Column(db.String(DEFAULT_VARCHAR_LENGTH))
    created_at = db.Column(db.DateTime())
    id_token = db.Column(db.String())

    user = db.relationship("User", backref="identities")

    @classmethod
    def from_token(cls, provider_id, provider_user_id, token, user=None):
        return cls(
            user=user,
            provider_id=provider_id,
            provider_user_id=provider_user_id,
            access_token=token["access_token"],
            created_at=datetime.utcfromtimestamp(token["created_at"]),
            id_token=token["id_token"],
        )
