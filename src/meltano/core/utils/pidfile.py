import psutil
from pathlib import Path
from typing import Union


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

        return self._pid

    def write_pid(self, pid: int):
        with self.path.open("w") as raw:
            raw.write(str(pid))
            self._pid = pid

    @property
    def process(self) -> psutil.Process:
        return psutil.Process(self.pid)

    def unlink(self):
        return self.path.unlink()

    def __str__(self) -> str:
        return str(self.path)
