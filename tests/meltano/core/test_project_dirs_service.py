from __future__ import annotations

import pytest

from meltano.core.project_dirs_service import ProjectDirsService


class TestProjectDirsService:
    @pytest.fixture
    def subject(self, tmp_path_factory: pytest.TempPathFactory) -> ProjectDirsService:
        root = tmp_path_factory.mktemp("project")
        sys_dir = tmp_path_factory.mktemp(".meltano")
        return ProjectDirsService(root=root, sys_dir=sys_dir)

    def test_ensure_cachedir_tag(
        self,
        subject: ProjectDirsService,
        subtests: pytest.Subtests,
    ) -> None:
        path = subject.sys_dir / "CACHEDIR.TAG"

        with subtests.test("creates file"):
            assert not path.exists()
            subject._ensure_cachedir_tag()
            assert path.read_text().startswith("Signature:")

        with subtests.test("preserves existing file"):
            path.write_text("Old content")
            subject._ensure_cachedir_tag()
            assert path.read_text() == "Old content"

    def test_ensure_gitignore(
        self,
        subject: ProjectDirsService,
        subtests: pytest.Subtests,
    ) -> None:
        path = subject.sys_dir / ".gitignore"

        with subtests.test("creates file"):
            assert not path.exists()
            subject._ensure_gitignore()
            assert path.read_text() == "*\n"

        with subtests.test("preserves existing file"):
            path.write_text("Old content")
            subject._ensure_gitignore()
            assert path.read_text() == "Old content"
