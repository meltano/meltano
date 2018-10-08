class Runner():
    def before_run(self, *args):
        pass

    def run(self, extractor_name, loader_name):
        pass

    def perform(self, *args):
        self.before_run(*args)
        self.run(*args)
