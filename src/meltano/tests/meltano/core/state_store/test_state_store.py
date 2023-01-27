from __future__ import annotations

import os
import shutil

import pytest

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.state_store import (
    AZStorageStateStoreManager,
    DBStateStoreManager,
    GCSStateStoreManager,
    LocalFilesystemStateStoreManager,
    S3StateStoreManager,
    StateBackend,
    state_store_manager_from_project_settings,
)


@pytest.fixture(scope="function")
def state_path(test_dir):
    yield os.path.join(test_dir, ".meltano", "state")
    shutil.rmtree(os.path.join(test_dir, ".meltano", "state"))


def test_state_store_manager_from_project_settings(project: Project, state_path: str):
    settings_service = ProjectSettingsService(project)

    settings_service.set(["state_backend", "uri"], StateBackend.SYSTEMDB)
    settings_service.set(["state_backend", "lock_timeout_seconds"], 10)
    db_state_store: DBStateStoreManager = state_store_manager_from_project_settings(
        settings_service
    )
    assert isinstance(db_state_store, DBStateStoreManager)

    # Local Filesystem
    settings_service.set(["state_backend", "uri"], f"file://{state_path}")
    file_state_store: LocalFilesystemStateStoreManager = (
        state_store_manager_from_project_settings(settings_service)
    )
    assert isinstance(file_state_store, LocalFilesystemStateStoreManager)
    assert file_state_store.state_dir == state_path

    # Azure
    settings_service.set(["state_backend", "uri"], "azure://some_container/some/path")
    settings_service.set(
        ["state_backend", "azure", "connection_string"], "SOME_CONNECTION_STRING"
    )
    az_state_store: AZStorageStateStoreManager = (
        state_store_manager_from_project_settings(settings_service)
    )
    assert isinstance(az_state_store, AZStorageStateStoreManager)
    assert az_state_store.container_name == "some_container"
    assert az_state_store.prefix == "/some/path"
    assert az_state_store.connection_string == "SOME_CONNECTION_STRING"

    # GCS
    settings_service.set(["state_backend", "uri"], "gs://some_container/some/path")
    gs_state_store: GCSStateStoreManager = state_store_manager_from_project_settings(
        settings_service
    )
    assert isinstance(gs_state_store, GCSStateStoreManager)
    assert gs_state_store.bucket == "some_container"
    assert gs_state_store.prefix == "/some/path"

    # AWS S3 (credentials in URI)
    settings_service.set(
        ["state_backend", "uri"],
        "s3://aws_access_key_id:aws_secret_access_key@some_bucket/some/path",
    )
    s3_state_store: S3StateStoreManager = state_store_manager_from_project_settings(
        settings_service
    )
    assert isinstance(s3_state_store, S3StateStoreManager)
    assert s3_state_store.bucket == "some_bucket"
    assert s3_state_store.prefix == "/some/path"
    assert s3_state_store.aws_access_key_id == "aws_access_key_id"  # noqa: S105
    assert s3_state_store.aws_secret_access_key == "aws_secret_access_key"  # noqa: S105

    # AWS S3 (credentials provided directly)
    settings_service.set(
        ["state_backend", "uri"],
        "s3://some_bucket/some/path",
    )
    settings_service.set(["state_backend", "s3", "aws_access_key_id"], "a_different_id")
    settings_service.set(
        ["state_backend", "s3", "aws_secret_access_key"], "a_different_key"
    )
    s3_state_store_direct_creds: S3StateStoreManager = (
        state_store_manager_from_project_settings(settings_service)
    )
    assert s3_state_store_direct_creds.aws_access_key_id == "a_different_id"
    assert (
        s3_state_store_direct_creds.aws_secret_access_key
        == "a_different_key"  # noqa: S105
    )
