import psutil
import logging
from pathlib import Path
from typing import Union


logger = logging.getLogger(__name__)


class PIDFile:
    def __init__(self, path: Union[str, Path]):
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

        logger.debug(f"Loaded PID {self._pid} from {self.path}")
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
        except psutil.NoSuchProcess:
            raise UnknownProcessError(self)

    def unlink(self):
        return self.path.unlink()

    def __str__(self) -> str:
        return str(self.path)


class UnknownProcessError(Exception):
    """Occurs when the PIDFile doesn't yield a readable PID."""

    def __init__(self, pid_file: PIDFile):
        self.pid_file = pid_file

        super().__init__(f"{pid_file} doesn't refer to a valid Process.")
