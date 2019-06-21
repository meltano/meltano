from abc import ABC, abstractmethod


class IncompatibleVersionError(Exception):
    """Occurs when a component is incompatible with its representation"""


class Versioned(ABC):
    """Mixin to represent something that must be compatible with a certain version"""

    @property
    @abstractmethod
    def backend_version(self) -> int:
        pass

    def is_compatible(self, version: int = None):
        try:
            self.ensure_compatible(version=version)
            return True
        except IncompatibleVersionError:
            return False

    def ensure_compatible(self, version: int = None):
        version = self.__class__.__version__ if version is None else version

        if self.backend_version > version:
            raise IncompatibleVersionError(
                f"Version {version} required, currently at {self.backend_version}"
            )
