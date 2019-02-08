import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED

from meltano.core.project import Project
from meltano.api.controllers.m5o_file_parser import MeltanoAnalysisFileParser
from meltano.core.compiler.acl_compiler import ACLCompiler


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, compiler):
        self.compiler = compiler

        super().__init__(ignore_patterns=["*.m5oc"])

    def on_any_event(self, event):
        self.compiler.compile()


class MeltanoBackgroundCompiler:
    def __init__(self, project: Project):
        self.project = project
        self.observer = self.setup_observer()

    @property
    def source_dir(self):
        return self.project.root.joinpath("model")

    def compile(self):
        output_dir = self.project.run_dir()

        try:
            acl_compiler = ACLCompiler(self.source_dir, output_dir)
            acl_compiler.compile()
            logging.info(f"ACL have been compiled.")
        except Exception:
            logging.error(f"Failed to compile ACL.")

        try:
            m5o_parse = MeltanoAnalysisFileParser(self.source_dir)
            models = m5o_parse.parse()
            m5o_parse.compile(models)
            logging.info(f"Models have been compiled.")
        except Exception:
            logging.warn(f"Failed to compile models.")

    def setup_observer(self):
        event_handler = CompileEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.source_dir), recursive=True)

        return observer

    def start(self):
        self.observer.start()
        logging.info(f"Auto-compiling models in {self.observer}.")

    def stop(self):
        self.observer.stop()
