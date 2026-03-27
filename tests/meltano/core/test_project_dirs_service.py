from __future__ import annotations

import pytest

from meltano.core.project_dirs_service import ProjectDirsService


class TestProjectDirsService:
    @pytest.fixture
    def subject(self, tmp_path_factory: pytest.TempPathFactory) -> ProjectDirsService:
        root = tmp_path_factory.mktemp("project")
        sys_dir = tmp_path_factory.mktemp(".meltano")
        return ProjectDirsService(root=root, sys_dir=sys_dir)

    def test_add_cachedir_tag(self, subject: ProjectDirsService) -> None:
        assert not subject.cachedir_tag.exists()
        subject.add_cachedir_tag()
        assert subject.cachedir_tag.exists()
