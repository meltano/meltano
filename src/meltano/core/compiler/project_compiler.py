import logging

from meltano.core.project import Project
from meltano.core.m5o.m5o_file_parser import (
    MeltanoAnalysisFileParser,
    MeltanoAnalysisFileParserError,
)


class ProjectCompiler:
    """
    Meltano projects have multiple .m5o files that need to be
    compiled.

    This component is responsible for the compilation of
    the whole Meltano project.
    """

    def __init__(self, project):
        self.project = project
        self._parsed = False

    @property
    def source_dir(self):
        return self.project.model_dir()

    def parse(self):
        self.parser = MeltanoAnalysisFileParser(self.project)
        try:
            self.topics = self.parser.parse()
            self.package_topics = self.parser.parse_packages()
            self._parsed = True
        except MeltanoAnalysisFileParserError as e:
            logging.warn(f"Failed to compile topics: {e}")
            raise e

    def compile(self):
        try:
            if not self._parsed:
                self.parse()
            if self.topics:
                self.parser.compile(self.topics)
            if self.package_topics:
                self.parser.compile(self.package_topics)
            logging.debug(f"Successfully compiled topics")
        except MeltanoAnalysisFileParserError as e:
            logging.warn(f"Failed to compile topics: {e}")
            raise e
