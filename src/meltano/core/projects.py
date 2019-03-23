from pathlib import Path


class Projects:
    def __init__(self, cwd):
        self.cwd = Path(cwd)

    def find(self):
        return [
            {"name": p.parent.parts[-1]}
            for p in self.cwd.glob("./*/meltano.yml")
        ]
