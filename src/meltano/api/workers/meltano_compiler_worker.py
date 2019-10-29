import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED
from meltano.core.project import Project
from meltano.core.compiler.project_compiler import ProjectCompiler


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, compiler):
        self.compiler = compiler

        super().__init__(ignore_patterns=["*.m5oc"])

    def on_any_event(self, event):
        try:
            self.compiler.compile()
        except Exception as e:
            logging.error(f"Compilation failed: {str(e)}")


class MeltanoCompilerWorker:
    def __init__(self, project: Project, compiler: ProjectCompiler = None):
        self.project = project
        self.compiler = compiler or ProjectCompiler(project)
        self.observer = self.setup_observer()

    @property
    def model_dir(self):
        return self.project.root_dir("model")

    def setup_observer(self):
        event_handler = CompileEventHandler(self.compiler)
        observer = Observer()
        observer.schedule(event_handler, str(self.model_dir), recursive=True)

        return observer

    def start(self):
        try:
            self.observer.start()
            logging.info(f"Auto-compiling models in '{self.model_dir}'")
        except OSError:
            # most probably INotify being full
            logging.warning(
                f"Model auto-compilation is disabled: INotify limit reached."
            )

    def stop(self):
        self.observer.stop()
