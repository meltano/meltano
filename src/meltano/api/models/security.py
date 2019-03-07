from flask_security import UserMixin, RoleMixin

from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role", secondary="roles_users", backref=db.backref("users", lazy="dynamic")
    )

    def __repr__(self):
        roles = ",".join(r.name for r in self.roles)
        return f"<User username={self.username} roles={roles}>"

    def __str__(self):
        roles = ",".join(r.name for r in self.roles)
        return f"@{self.username}({roles})"

    def canonical(self, _scopes):
        return self.username


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))


class RolePermissions(db.Model):
    __tablename__ = "role_permissions"
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
    type = db.Column(db.String())
    context = db.Column(db.String())
    role = db.relationship("Role", backref="permissions")

    def canonical(self, scopes=[]):
        canonical = {
            "role_id": self.role_id,
            "type": self.type,
            "context": self.context,
        }

        if Role in scopes:
            del canonical["role_id"]

        return canonical


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __eq__(self, other):
        if isinstance(other, Role):
            return super().__eq__(other)

        return self.name == other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"<Role({self.name})>"

    def canonical(self, _scopes):
        return self.name
