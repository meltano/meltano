import logging

import fasteners
import threading

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
        self._lock = threading.Lock()

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
            logging.warning(f"Failed to compile topics: {e}")
            raise e

    @fasteners.locked
    def compile(self):
        try:
            self.parse()

            all_topics = self.topics + self.package_topics
            if all_topics:
                self.parser.compile(all_topics)

            logging.debug(f"Successfully compiled topics")
        except MeltanoAnalysisFileParserError as e:
            logging.warning(f"Failed to compile topics: {e}")
            raise e
