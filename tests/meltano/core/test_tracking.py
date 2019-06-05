import pytest
import os


@pytest.mark.meta
def test_tracking_disabled():
    assert os.getenv("MELTANO_DISABLE_TRACKING") == "True"
