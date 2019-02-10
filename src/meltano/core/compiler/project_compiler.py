import logging

from meltano.core.project import Project
from .acl_compiler import ACLCompiler

# TODO 2019-02: move to `meltano.core`
from meltano.api.controllers.m5o_file_parser import MeltanoAnalysisFileParser


class ProjectCompiler:
    def __init__(self, project):
        self.project = project

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
