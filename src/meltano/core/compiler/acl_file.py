from typing import Dict
from copy import copy
from .m5oc_file import M5ocFile


class Permission():
    """Wraps a permission definition"""
    def __init__(self, name, definition: Dict):
        self.name = name
        self.content = definition

    def can(self, role: str, target: str, declaration: str = None):
        declaration = declaration if declaration in self.content[target] else "_default"

        return role in self.content[target].get(declaration, [])


class ACLFile(M5ocFile):
    def roles(self, role: str = None):
        if role:
            return copy(self.content["roles"][role])

        return copy(self.content["roles"])

    def permissions(self, permission: str = None):
        if permission:
            return Permission(permission, self.content["acl"][permission])

        return [Permission(permission, permission_def)
                for permission, permission_def in self.content["acl"].items()]

    def can(self, role: str, permission: str, target: str, declaration: str = None):
        return self.permissions(permission).can(role, target, declaration)
