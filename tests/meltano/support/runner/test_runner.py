import pytest
import os
import json

from unittest import mock
from meltano.support.job import Job, State
from meltano.support.runner.singer import SingerRunner
from pathlib import Path


TEST_JOB_ID = "test_job"
TAP_NAME = "tap-test"
TARGET_NAME = "target-test"


def create_tap_files(config_dir: Path, tap=TAP_NAME):
    for file in (f"{tap}.config.json", f"{tap}.properties.json"):
        Path(os.path.join(config_dir, file)).touch()

    return config_dir


def create_target_files(config_dir: Path, target=TARGET_NAME):
    Path(os.path.join(config_dir, f"{target}.config.json")).touch()

    return config_dir


@pytest.fixture()
def subject(db_setup, mkdtemp):
    tap_config_dir = mkdtemp()
    target_config_dir = mkdtemp()

    create_tap_files(tap_config_dir)
    create_target_files(target_config_dir)

    Job(elt_uri=TEST_JOB_ID,
        state=State.SUCCESS,
        payload={
            'singer_state': {"bookmarks": []}
        }).save()

    return SingerRunner(TEST_JOB_ID,
                        tap_config_dir=tap_config_dir,
                        target_config_dir=target_config_dir)


def test_prepare_job(subject):
    subject.prepare(TAP_NAME, TARGET_NAME)

    for f in subject.tap_files.values():
        assert(f.exists())
    for f in subject.target_files.values():
        assert(f.exists())


@mock.patch('subprocess.Popen')
def test_invoke(Popen, subject):
    called_bins = []
    def Popen_record_bin(cmd, *args, **kwargs):
        called_bins.append(list(cmd)[0])
        return mock.DEFAULT

    # mock Popen and make sure the paths are valid
    process_mock = mock.Mock()
    process_mock.wait.return_value = 0
    Popen.return_value = process_mock
    Popen.side_effect = Popen_record_bin

    subject.invoke(TAP_NAME, TARGET_NAME)

    tap_bin = str(subject.exec_path(TAP_NAME))
    target_bin = str(subject.exec_path(TARGET_NAME))
    assert(called_bins == [target_bin, "tee", tap_bin])
    assert(process_mock.wait.call_count == 2)


def test_bookmark(subject):
    with subject.target_files['state'].open("w") as state:
        state.write('{"line": 1}\n')
        state.write('{"line": 2}\n')

    subject.bookmark()
    assert(subject.job.payload['singer_state']['line'] == 2)
