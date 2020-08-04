class RunnerError(Exception):
    def __init__(self, message, exitcodes={}):
        super().__init__(message)
        self.exitcodes = exitcodes


class Runner:
    def run(self):
        pass
