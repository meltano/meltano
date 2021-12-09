import os

import pytest

from meltano.core.project_settings_service import ProjectSettingsService


@pytest.mark.meta
def test_tracking_disabled(project):
    assert os.getenv("MELTANO_DISABLE_TRACKING") == "True"
    assert ProjectSettingsService(project).get("send_anonymous_usage_stats") == False
