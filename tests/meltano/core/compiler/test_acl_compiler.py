import pytest
from pathlib import Path

from meltano.core.compiler.acl_compiler import ACLCompiler
from meltano.core.compiler.acl_file import ACLFile


@pytest.fixture
def compiler(project):
    compiler = ACLCompiler(project.root.joinpath("model"),
                           project.root.joinpath("model"))

    return compiler


class TestACLCompiler:
    @pytest.fixture
    def subject(self, compiler):
        return compiler

    def test_sources(self, project, subject):
        sources = list(subject.sources())

        assert sources == [Path(project.root.joinpath("model", "acls.m5o"))]

    def test_compile(self, subject):
        subject.compile()
        compiled_path = Path(subject.output_path)

        assert compiled_path.exists()


class TestACLFile:
    @pytest.fixture
    def subject(self, compiler):
        compiler.compile()
        return ACLFile.load(compiler.output_path.open())

    def test_can(self, subject):
        view = subject.permissions("view")
        assert subject.can("admin", "view", "reports")
