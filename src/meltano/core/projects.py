import os
from pathlib import Path


class Projects:
    def __init__(self, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        self.cwd = Path(cwd)
        self.meltano_projects_dir = self.cwd.joinpath(".meltano_projects")
        if not self.meltano_projects_dir.exists():
            self.create_meltano_projects_dir()

    def create_meltano_projects_dir(self):
        self.meltano_projects_dir.mkdir(parents=False, exist_ok=False)

    def find(self):
        return [{"name": p.parent.parts[-1]} for p in self.cwd.glob("./*/meltano.yml")]
