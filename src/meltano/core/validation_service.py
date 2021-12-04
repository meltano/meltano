"""Class for invoking plugin validations."""

from enum import Enum
from typing import Dict

from meltano.core.plugin_invoker import PluginInvoker
from sqlalchemy.orm.session import sessionmaker

try:
    from typing import Protocol  # noqa:  WPS433
except ImportError:
    from typing_extensions import Protocol  # noqa:  WPS433,WPS440

EXIT_CODE_OK = 0


class ValidationOutcome(str, Enum):
    """Data validation outcome options."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

    @property
    def color(self) -> str:
        """Return terminal color for this outcome."""
        return "green" if self == self.SUCCESS else "red"

    @classmethod
    def from_exit_code(cls, exit_code: int):
        """Create validation outcome from an exit code."""
        return cls.SUCCESS if exit_code == EXIT_CODE_OK else cls.FAILURE


class ValidatorProtocol(Protocol):
    """Interface for all validators."""

    @property
    def name(self) -> str:
        """Retrive validator name."""
        ...

    @property
    def selected(self) -> bool:
        """Retrive whether validator is selected to run."""
        ...

    async def run_async(self, invoker: PluginInvoker) -> int:
        """Run validator."""
        ...


class ValidationsRunner:
    """Class to collect all validations defined for a plugin."""

    def __init__(
        self,
        invoker: PluginInvoker,
        validators: Dict[str, ValidatorProtocol],
    ) -> None:
        """Create a validators runner for a plugin."""
        self.invoker = invoker
        self.validators = validators

    @property
    def plugin_name(self) -> str:
        """Get underlying plugin name."""
        return self.invoker.plugin.name

    def select_test(self, name: str) -> None:
        """Mark a single test as selected.

        Args:
            name: Test (command) name.

        Raises:
            KeyError: If plugin test is not defined.
        """
        try:
            self.validators[name].selected = True
        except KeyError as exc:
            raise KeyError(
                f"Plugin {self.plugin_name} does not have a test named '{name}'"
            ) from exc

    def select_all(self) -> None:
        """Mark all plugin validators as selected."""
        for name in self.validators.keys():
            self.validators[name].selected = True

    async def run_all(self, session: sessionmaker) -> Dict[str, int]:
        """Run all validators defined in a plugin.

        Args:
            session: A SQLAlchemy ORM session.

        Returns:
            A mapping of validator names to exit codes.
        """
        results = {}
        async with self.invoker.prepared(session):
            for name, validation in self.validators.items():
                if validation.selected:
                    results[name] = await validation.run_async(self.invoker)
        return results
