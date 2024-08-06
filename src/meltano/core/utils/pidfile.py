from __future__ import annotations  # noqa: D100

from pathlib import Path

import psutil
import structlog

logger = structlog.stdlib.get_logger(__name__)


class PIDFile:  # noqa: D101
    def __init__(self, path: str | Path):  # noqa: D107
        self.path = Path(path)
        self._pid = None

    @property
    def pid(self):  # noqa: ANN201, D102
        return self._pid or self.load_pid()

    def load_pid(self) -> int:  # noqa: D102
        try:
            with self.path.open("r") as raw:
                self._pid = int(raw.read())
        except ValueError:
            self.path.unlink()
        except FileNotFoundError:
            pass

        logger.debug(f"Loaded PID {self._pid} from {self.path}")  # noqa: G004
        return self._pid

    def write_pid(self, pid: int) -> None:  # noqa: D102
        with self.path.open("w") as raw:
            raw.write(str(pid))
            self._pid = pid

    @property
    def process(self) -> psutil.Process:  # noqa: D102
        if self.pid is None:
            raise UnknownProcessError(self)

        try:
            return psutil.Process(self.pid)
        except psutil.NoSuchProcess as ex:
            raise UnknownProcessError(self) from ex

    def unlink(self):  # noqa: ANN201, D102
        return self.path.unlink()

    def __str__(self) -> str:  # noqa: D105
        return str(self.path)


class UnknownProcessError(Exception):
    """The PIDFile doesn't yield a readable PID."""

    def __init__(self, pid_file: PIDFile):  # noqa: D107
        self.pid_file = pid_file

        super().__init__(f"{pid_file} doesn't refer to a valid Process.")
