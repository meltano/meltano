from __future__ import annotations


class RunnerError(Exception):
    def __init__(self, message, exitcodes=None):
        super().__init__(message)
        self.exitcodes = {} if exitcodes is None else exitcodes


class Runner:
    def run(self):
        pass
