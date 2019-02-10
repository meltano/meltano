from typing import Dict, List
from copy import copy
from .m5oc_file import M5ocFile


class Permission:
    """Wraps a permission definition"""

    def __init__(self, name, definition: Dict):
        self.name = name
        self.content = definition

    def can(self, role: str, target: str, declaration: str = None):
        declaration = declaration if declaration in self.content[target] else "_default"

        return role in self.content[target].get(declaration, [])

    def __repr__(self):
        return f"<Permission name={self.name}>"


class Role:
    """Wraps a role definition"""

    def __init__(self, name, users: List[str]):
        self.name = name
        self._users = users

    @property
    def users(self):
        return copy(self._users)

    def __eq__(self, other):
        return self.name == str(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Role name={self.name}>"


class ACLFile(M5ocFile):
    def roles(self, role: str = None):
        if role:
            return Role(role, self.content["roles"][role])

        return [Role(role, users) for role, users in self.content["roles"].items()]

    def permissions(self, permission: str = None):
        if permission:
            return Permission(permission, self.content["acl"][permission])

        return [
            Permission(permission, permission_def)
            for permission, permission_def in self.content["acl"].items()
        ]

    def can(self, role: str, permission: str, target: str, declaration: str = None):
        return self.permissions(permission).can(role, target, declaration)
