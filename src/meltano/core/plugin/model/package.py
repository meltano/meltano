from pathlib import Path


class Package:
    def __init__(self, name, project):
        self.name = name
        self.project = project

    @property
    def tables(self):
        return self.package_model_dir(".table")

    @property
    def topics(self):
        return self.package_model_dir(".topic")

    @property
    def files(self):
        return self.project.model_dir().glob(f"{self.name}/**/*.m5o")

    def package_model_dir(self, file_type):
        return [
            Path(f)
            for f in self.project.model_dir().glob(f"{self.name}/**/*{file_type}.m5o")
        ]
