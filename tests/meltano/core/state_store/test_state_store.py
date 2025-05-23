from __future__ import annotations

import shutil
import sys
import typing as t
from unittest import mock

import moto
import pytest
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob._shared.authentication import (
    SharedKeyCredentialPolicy,
)
from google.auth.credentials import AnonymousCredentials
from google.cloud.exceptions import NotFound
from google.cloud.storage import Blob

from fixtures.state_backends import DummyStateStoreManager
from meltano.core.error import MeltanoError
from meltano.core.state_store import (
    SYSTEMDB,
    DBStateStoreManager,
    MeltanoState,
    StateBackend,
    state_store_manager_from_project_settings,
)
from meltano.core.state_store.azure import AZStorageStateStoreManager
from meltano.core.state_store.filesystem import _LocalFilesystemStateStoreManager
from meltano.core.state_store.google import GCSStateStoreManager
from meltano.core.state_store.s3 import S3StateStoreManager

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.project import Project

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoint, EntryPoints
else:
    from importlib_metadata import EntryPoint, EntryPoints


def test_unknown_state_backend_scheme(project: Project):
    project.settings.set(["state_backend", "uri"], "unknown://")
    with pytest.raises(ValueError, match="No state backend found for scheme"):
        state_store_manager_from_project_settings(project.settings)


def test_pluggable_state_backend(project: Project, monkeypatch: pytest.MonkeyPatch):
    project.settings.set(["state_backend", "uri"], "custom://")

    entry_points = EntryPoints(
        (
            EntryPoint(
                value="fixtures.state_backends:DummyStateStoreManager",
                name="custom",
                group="meltano.state_backends",
            ),
        ),
    )

    with monkeypatch.context() as m:
        m.setattr(StateBackend.addon, "installed", entry_points)
        assert "custom" in StateBackend.backends()

        state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(state_store, DummyStateStoreManager)


class TestSystemDBStateBackend:
    def test_manager_from_settings(self, project: Project) -> None:
        project.settings.set(["state_backend", "uri"], SYSTEMDB)
        project.settings.set(["state_backend", "lock_timeout_seconds"], 10)
        db_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(db_state_store, DBStateStoreManager)


class TestLocalFilesystemStateBackend:
    @pytest.fixture
    def state_path(self, tmp_path: Path):
        path = tmp_path / ".meltano" / "state"
        try:
            yield str(path)
        finally:
            shutil.rmtree(path)

    def test_manager_from_settings(self, project: Project, state_path: str) -> None:
        project.settings.set(["state_backend", "uri"], f"file://{state_path}")
        file_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(file_state_store, _LocalFilesystemStateStoreManager)
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
    @pytest.fixture
    def manager(self, project: Project) -> GCSStateStoreManager:
        project.settings.set(["state_backend", "uri"], "gs://my-bucket")
        return state_store_manager_from_project_settings(project.settings)

    def test_manager_from_settings(self, project: Project) -> None:
        # GCS
        project.settings.set(["state_backend", "uri"], "gs://some_container/some/path")
        gs_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(gs_state_store, GCSStateStoreManager)
        assert gs_state_store.bucket == "some_container"
        assert gs_state_store.prefix == "/some/path"

    def test_delete_error(
        self,
        manager: GCSStateStoreManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        file_path = "some/path"

        def _not_found(*args, **kwargs):  # noqa: ARG001
            raise NotFound("No such object: ...")  # noqa: EM101

        def _other_error(*args, **kwargs):  # noqa: ARG001
            raise RuntimeError("Something went wrong")  # noqa: EM101

        # Mock default credentials
        mock_credentials = AnonymousCredentials()

        with (
            mock.patch(
                "google.auth.default",
                return_value=(mock_credentials, "mock-project"),
            ),
            monkeypatch.context() as m,
        ):
            m.setattr(Blob, "delete", _not_found)
            manager.delete_file(file_path)

            m.setattr(Blob, "delete", _other_error)
            with pytest.raises(RuntimeError, match="Something went wrong"):
                manager.delete_file(file_path)

    @pytest.mark.parametrize(
        ("components", "result"),
        (
            pytest.param(["a", "b", "c"], "a/b/c"),
            pytest.param(["a", "b", "c", ""], "a/b/c"),
            pytest.param(["a", "b", "", "c"], "a/b/c"),
            pytest.param(["", "a", "b", "c"], "a/b/c"),
        ),
    )
    def test_join_path(
        self,
        manager: GCSStateStoreManager,
        components: list[str],
        result: str,
    ) -> None:
        assert manager.join_path(*components) == result


class TestS3StateBackend:
    @pytest.fixture
    def bucket(self) -> str:
        return "some_bucket"

    @pytest.fixture
    def prefix(self) -> str:
        return "some/path"

    @pytest.fixture
    def aws_access_key_id(self) -> str:
        return "aws_access_key_id"

    @pytest.fixture
    def aws_secret_access_key(self) -> str:
        return "aws_secret_access_key"

    @pytest.fixture
    def s3_uri(
        self,
        bucket: str,
        prefix: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ) -> str:
        return f"s3://{aws_access_key_id}:{aws_secret_access_key}@{bucket}/{prefix}"

    def test_manager_from_settings(
        self,
        project: Project,
        bucket: str,
        prefix: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        s3_uri: str,
    ) -> None:
        # AWS S3 (credentials in URI)
        project.settings.set(["state_backend", "uri"], s3_uri)
        s3_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(s3_state_store, S3StateStoreManager)
        assert s3_state_store.bucket == bucket
        assert s3_state_store.prefix == f"/{prefix}"
        assert s3_state_store.aws_access_key_id == aws_access_key_id
        assert s3_state_store.aws_secret_access_key == aws_secret_access_key

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

    def test_get(
        self,
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
        bucket: str,
        prefix: str,
        s3_uri: str,
    ) -> None:
        project.settings.set(["state_backend", "uri"], s3_uri)

        s3_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(s3_state_store, S3StateStoreManager)

        state_id = "test_state_id"
        state = MeltanoState(state_id=state_id, completed_state={"key": "value"})

        with moto.mock_aws():
            monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
            monkeypatch.delenv("AWS_PROFILE", raising=False)
            s3_state_store.client.create_bucket(Bucket=bucket)

            state_key = f"{prefix}/{state_id}/state.json"
            s3_state_store.client.put_object(
                Bucket=bucket,
                Key=state_key,
                Body=state.json(),
                ContentType="application/json",
            )

            assert s3_state_store.get(state_id=state_id) == state

    def test_set(
        self,
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
        bucket: str,
        prefix: str,
        s3_uri: str,
    ) -> None:
        project.settings.set(["state_backend", "uri"], s3_uri)

        s3_state_store = state_store_manager_from_project_settings(project.settings)
        assert isinstance(s3_state_store, S3StateStoreManager)

        state_id = "test_state_id"
        state = MeltanoState(state_id=state_id, completed_state={"key": "value"})

        with moto.mock_aws():
            monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
            monkeypatch.delenv("AWS_PROFILE", raising=False)
            s3_state_store.client.create_bucket(Bucket=bucket)

            s3_state_store.set(state)

            state_key = f"{prefix}/{state_id}/state.json"
            response = s3_state_store.client.get_object(Bucket=bucket, Key=state_key)
            assert (
                MeltanoState.from_file(
                    state_id=state_id,
                    file_obj=response["Body"],
                )
                == state
            )
            assert response["ContentType"] == "application/json"
