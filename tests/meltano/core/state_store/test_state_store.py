from __future__ import annotations

import shutil
import typing as t

import pytest
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob._shared.authentication import (
    SharedKeyCredentialPolicy,
)

from meltano.core.error import MeltanoError
from meltano.core.state_store import (
    AZStorageStateStoreManager,
    DBStateStoreManager,
    GCSStateStoreManager,
    LocalFilesystemStateStoreManager,
    S3StateStoreManager,
    StateBackend,
    state_store_manager_from_project_settings,
)

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project


class TestSystemDBStateBackend:
    def test_manager_from_settings(self, project: Project) -> None:
        project.settings.set(["state_backend", "uri"], StateBackend.SYSTEMDB)
        project.settings.set(["state_backend", "lock_timeout_seconds"], 10)
        db_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(db_state_store, DBStateStoreManager)


class TestLocalFilesystemStateBackend:
    @pytest.fixture()
    def state_path(self, tmp_path: Path):
        path = tmp_path / ".meltano" / "state"
        try:
            yield str(path)
        finally:
            shutil.rmtree(path)

    def test_manager_from_settings(self, project: Project, state_path: str) -> None:
        project.settings.set(["state_backend", "uri"], f"file://{state_path}")
        file_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(file_state_store, LocalFilesystemStateStoreManager)
        assert file_state_store.state_dir == state_path


class TestAzureStateBackend:
    def test_manager_from_settings(self, project: Project) -> None:
        # Azure
        project.settings.set(
            ["state_backend", "uri"],
            "azure://some_container/some/path",
        )
        project.settings.set(
            ["state_backend", "azure", "connection_string"],
            "SOME_CONNECTION_STRING",
        )
        project.settings.set(
            ["state_backend", "azure", "storage_account_url"],
            "SOME_STORAGE_ACCOUNT_URL",
        )
        az_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(az_state_store, AZStorageStateStoreManager)
        assert az_state_store.container_name == "some_container"
        assert az_state_store.prefix == "/some/path"
        assert az_state_store.connection_string == "SOME_CONNECTION_STRING"
        assert az_state_store.storage_account_url == "SOME_STORAGE_ACCOUNT_URL"

        # Azure, missing container name
        project.settings.set(["state_backend", "uri"], "azure://")
        with pytest.raises(MeltanoError):
            state_store_manager_from_project_settings(project.settings)

        # Azure, missing connection string
        project.settings.set(
            ["state_backend", "uri"],
            "azure://some_container/some/path",
        )
        project.settings.unset(["state_backend", "azure", "connection_string"])
        az_state_store = state_store_manager_from_project_settings(project.settings)
        # Should create client using default creds
        assert isinstance(az_state_store, AZStorageStateStoreManager)
        assert isinstance(az_state_store.client, BlobServiceClient)
        assert isinstance(az_state_store.client.credential, DefaultAzureCredential)

        # Azure, missing storage account url
        project.settings.unset(["state_backend", "azure", "storage_account_url"])
        project.settings.set(
            ["state_backend", "azure", "connection_string"],
            (
                "DefaultEndpointsProtocol=https;"
                "AccountName=myAccount;"
                "AccountKey=myAccountKey"
            ),
        )
        az_state_store = state_store_manager_from_project_settings(project.settings)

        # Should create client using connection string
        assert isinstance(az_state_store, AZStorageStateStoreManager)
        assert isinstance(az_state_store.client, BlobServiceClient)
        assert isinstance(az_state_store.client.credential, SharedKeyCredentialPolicy)

        # Azure, missing connection string and storage account url
        project.settings.unset(["state_backend", "azure", "connection_string"])
        project.settings.unset(["state_backend", "azure", "storage_account_url"])
        az_state_store = state_store_manager_from_project_settings(project.settings)

        assert isinstance(az_state_store, AZStorageStateStoreManager)
        # Should raise error
        with pytest.raises(MeltanoError):
            _ = az_state_store.client


class TestGCSStateBackend:
    def test_manager_from_settings(self, project: Project) -> None:
        # GCS
        project.settings.set(["state_backend", "uri"], "gs://some_container/some/path")
        gs_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(gs_state_store, GCSStateStoreManager)
        assert gs_state_store.bucket == "some_container"
        assert gs_state_store.prefix == "/some/path"


class TestS3StateBackend:
    def test_manager_from_settings(self, project: Project) -> None:
        # AWS S3 (credentials in URI)
        project.settings.set(
            ["state_backend", "uri"],
            "s3://aws_access_key_id:aws_secret_access_key@some_bucket/some/path",
        )
        s3_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(s3_state_store, S3StateStoreManager)
        assert s3_state_store.bucket == "some_bucket"
        assert s3_state_store.prefix == "/some/path"
        assert s3_state_store.aws_access_key_id == "aws_access_key_id"
        assert (
            s3_state_store.aws_secret_access_key == "aws_secret_access_key"  # noqa: S105
        )

        # AWS S3 (credentials provided directly)
        project.settings.set(
            ["state_backend", "uri"],
            "s3://some_bucket/some/path",
        )
        project.settings.set(
            ["state_backend", "s3", "aws_access_key_id"],
            "a_different_id",
        )
        project.settings.set(
            ["state_backend", "s3", "aws_secret_access_key"],
            "a_different_key",
        )
        s3_state_store_direct_creds = state_store_manager_from_project_settings(
            project.settings,
        )
        assert isinstance(s3_state_store_direct_creds, S3StateStoreManager)
        assert s3_state_store_direct_creds.aws_access_key_id == "a_different_id"
        assert (
            s3_state_store_direct_creds.aws_secret_access_key == "a_different_key"  # noqa: S105
        )
