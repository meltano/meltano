import logging

from meltano.core.project import Project
from meltano.core.m5o.m5o_file_parser import MeltanoAnalysisFileParser


class ProjectCompiler:
    """
    Meltano projects have multiple .m5o files that need to be
    compiled.

    This component is responsible for the compilation of
    the whole Meltano project.
    """

    def __init__(self, project):
        self.project = project

    @property
    def source_dir(self):
        return self.project.root.joinpath("model")

    def compile(self):
        output_dir = self.project.run_dir()

        try:
            m5o_parse = MeltanoAnalysisFileParser(self.source_dir)
            models = m5o_parse.parse()
            m5o_parse.compile(models)
            logging.info(f"Models have been compiled.")
        except Exception:
            logging.warn(f"Failed to compile models.")
