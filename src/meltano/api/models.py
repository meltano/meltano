from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime


db = SQLAlchemy()


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role", secondary="roles_users", backref=db.backref("users", lazy="dynamic")
    )


# TODO: sync with the `acls.m5o`
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class OAuth(db.Model):
    __tablename__ = "oauth"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime())
    id_token = db.Column(db.String())
    # secret = db.Column(db.String(255))
    # display_name = db.Column(db.String(255))
    # profile_url = db.Column(db.String(512))
    # image_url = db.Column(db.String(512))
    # rank = db.Column(db.Integer)

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
