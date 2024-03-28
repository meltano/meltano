from __future__ import annotations

from pathlib import Path

import psutil
import structlog

logger = structlog.stdlib.get_logger(__name__)


class PIDFile:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._pid = None

    @property
    def pid(self):
        return self._pid or self.load_pid()

    def load_pid(self) -> int:
        try:
            with self.path.open("r") as raw:
                self._pid = int(raw.read())
        except ValueError:
            self.path.unlink()
        except FileNotFoundError:
            pass

        logger.debug(f"Loaded PID {self._pid} from {self.path}")  # noqa: G004
        return self._pid

    def write_pid(self, pid: int):
        with self.path.open("w") as raw:
            raw.write(str(pid))
            self._pid = pid

    @property
    def process(self) -> psutil.Process:
        if self.pid is None:
            raise UnknownProcessError(self)

        try:
            return psutil.Process(self.pid)
        except psutil.NoSuchProcess as ex:
            raise UnknownProcessError(self) from ex

    def unlink(self):
        return self.path.unlink()

    def __str__(self) -> str:
        return str(self.path)


class UnknownProcessError(Exception):
    """The PIDFile doesn't yield a readable PID."""

    def __init__(self, pid_file: PIDFile):
        self.pid_file = pid_file

        super().__init__(f"{pid_file} doesn't refer to a valid Process.")
