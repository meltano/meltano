from meltano.support.db import DB, SystemModel


class Runner():
    def before_run(self, *args):
        SystemModel.metadata.create_all(DB.default.engine)

    def run(self, extractor_name, loader_name):
        pass

    def perform(self, *args):
        self.before_run(*args)
        self.run(*args)
