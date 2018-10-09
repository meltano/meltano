import pytest
import os
import tempfile

from unittest import mock
from meltano.support.job import Job, State
from meltano.support.runner.singer import SingerRunner
from pathlib import Path

TEST_JOB_ID="test_job"


def create_tap_files(tap: str):
    dir = tempfile.mkdtemp()
    tap_config_dir = os.path.join(dir, tap)
    os.mkdir(tap_config_dir)

    for file in (f"{tap}.config.json", f"{tap}.properties.json"):
        Path(os.path.join(tap_config_dir, file)).touch()

    return tap_config_dir


def create_target_files(target: str):
    dir = tempfile.mkdtemp()
    target_config_dir = os.path.join(dir, target)
    os.mkdir(target_config_dir)
    Path(os.path.join(target_config_dir, f"{target}.config.json")).touch()

    return target_config_dir


@mock.patch.dict(os.environ, {
    'SINGER_TAP_CONFIG_DIR': create_tap_files("tap-test"),
    'SINGER_TARGET_CONFIG_DIR': create_target_files("target-test"),
})
def test_prepare_job(session):
    Job(elt_uri=TEST_JOB_ID,
        state=State.SUCCESS,
        payload={'singer_state': {"bookmarks": []}},
    ).save()

    subject = SingerRunner(TEST_JOB_ID)
    subject.prepare("tap-test", "target-test")

    assert(subject.tap_files['state'].exists())
