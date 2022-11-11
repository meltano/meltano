from __future__ import annotations

import datetime
import json
import os
import platform
import shutil
import string
from base64 import b64encode
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob._models import BlobProperties
from boto3 import client
from botocore.stub import Stubber
from dateutil.tz import tzutc
from google.cloud.storage import Blob, Bucket

from meltano.core.job_state import JobState
from meltano.core.state_store import (
    AZStorageStateStoreManager,
    GCSStateStoreManager,
    LocalFilesystemStateStoreManager,
    S3StateStoreManager,
    WindowsFilesystemStateStoreManager,
)


def on_windows() -> bool:
    return "Windows" in platform.system()


def encode_if_on_windows(string: str) -> str:
    if on_windows():
        return b64encode(string.encode()).decode()
    return string


class TestLocalFilesystemStateStoreManager:
    @pytest.fixture(scope="function")
    def subject(self, function_scoped_test_dir):
        if on_windows():
            yield WindowsFilesystemStateStoreManager(
                uri=f"file://{function_scoped_test_dir}\\.meltano\\state\\",
                lock_timeout_seconds=10,
            )
        else:
            yield LocalFilesystemStateStoreManager(
                uri=f"file://{function_scoped_test_dir}/.meltano/state/",
                lock_timeout_seconds=10,
            )

    @pytest.fixture(scope="function")
    def state_path(
        self, function_scoped_test_dir, subject: LocalFilesystemStateStoreManager
    ):
        Path(subject.state_dir).mkdir(parents=True, exist_ok=True)
        yield os.path.join(function_scoped_test_dir, ".meltano", "state")
        shutil.rmtree(
            os.path.join(function_scoped_test_dir, ".meltano", "state"),
            ignore_errors=True,
        )

    def test_join_path(self, subject: LocalFilesystemStateStoreManager):
        if on_windows():
            assert subject.join_path("a", "b") == "a\\b"
            assert subject.join_path("a", "b", "c", "d", "e") == "a\\b\\c\\d\\e"
        else:
            assert subject.join_path("a", "b") == "a/b"
            assert subject.join_path("a", "b", "c", "d", "e") == "a/b/c/d/e"

    def test_create_state_id_dir_if_not_exists(
        self, subject: LocalFilesystemStateStoreManager, state_path
    ):
        state_id_path = os.path.join(
            state_path, encode_if_on_windows("create_state_id_dir")
        )
        assert not os.path.exists(state_id_path)
        subject.create_state_id_dir_if_not_exists("create_state_id_dir")
        assert os.path.exists(state_id_path)

    def test_get_reader(self, subject: LocalFilesystemStateStoreManager, state_path):
        filepath = os.path.join(state_path, "get_reader")
        open(filepath, "a").close()  # noqa: WPS515
        with subject.get_reader(path=filepath) as reader:
            assert reader.name == filepath

    def test_get_writer(self, subject: LocalFilesystemStateStoreManager, state_path):
        filepath = os.path.join(state_path, "get_writer")
        with subject.get_writer(path=filepath) as writer:
            assert writer.name == filepath

    def test_get_state_path(
        self, subject: LocalFilesystemStateStoreManager, state_path
    ):
        assert subject.get_state_path("get_state_path") == os.path.join(
            state_path, encode_if_on_windows("get_state_path"), "state.json"
        )

    def test_get_lock_path(self, subject: LocalFilesystemStateStoreManager, state_path):
        assert subject.get_lock_path("some_state_id") == os.path.join(
            state_path, encode_if_on_windows("some_state_id"), "lock"
        )

    def test_acquire_lock(self, subject: LocalFilesystemStateStoreManager, state_path):
        dir_path = os.path.join(state_path, encode_if_on_windows("acquire_lock"))
        with subject.acquire_lock("acquire_lock"):
            assert os.path.exists(os.path.join(dir_path, "lock"))

    def test_get_state_ids(self, subject: LocalFilesystemStateStoreManager, state_path):
        dev_ids = [f"dev:{letter}-to-{letter}" for letter in string.ascii_lowercase]
        prod_ids = [f"prod:{letter}-to-{letter}" for letter in string.ascii_lowercase]
        for state_id in dev_ids + prod_ids:
            Path(subject.get_path(state_id)).mkdir(parents=True)
            open(  # noqa: WPS515
                subject.get_path(state_id, filename="state.json"), "w+"
            ).close()
        assert set(dev_ids + prod_ids) == set(subject.get_state_ids())

    def test_get(
        self,
        subject: LocalFilesystemStateStoreManager,
        state_path,
        state_ids_with_expected_states,
    ):
        for (state_id, expected_state) in state_ids_with_expected_states:
            state_dir = os.path.join(state_path, encode_if_on_windows(state_id))
            Path(state_dir).mkdir(parents=True)
            with open(  # noqa: WPS515
                os.path.join(state_dir, "state.json"), "w+"
            ) as state_file:
                json.dump(expected_state, state_file)

        for (state_id, expected_state) in state_ids_with_expected_states:
            assert subject.get(state_id) == JobState.from_json(
                state_id, json.dumps(expected_state)
            )

    def test_set(
        self,
        subject: LocalFilesystemStateStoreManager,
        state_path,
        state_ids_with_expected_states,
    ):
        for (state_id, expected_state) in state_ids_with_expected_states:
            subject.set(
                JobState.from_json(state_id, json.dumps({"completed": expected_state})),
            )
        for (state_id, expected_state) in state_ids_with_expected_states:
            with open(
                os.path.join(state_path, encode_if_on_windows(state_id), "state.json")
            ) as state_file:
                assert JobState.from_json(
                    state_id, json.dumps({"completed": expected_state})
                ) == JobState.from_file(state_id, state_file)

    def test_delete(
        self,
        subject: LocalFilesystemStateStoreManager,
        state_path,
        state_ids_with_expected_states,
    ):
        # Delete files
        state_id, expected_state = state_ids_with_expected_states[0]
        state_dir = os.path.join(state_path, encode_if_on_windows(state_id))
        Path(state_dir).mkdir(parents=True)
        filepath = os.path.join(state_dir, "state.json")
        with open(filepath, "w+") as state_file:
            json.dump(expected_state, state_file)
        assert os.path.exists(filepath)
        subject.delete(filepath)
        assert not os.path.exists(filepath)

        # Delete directories
        assert os.path.exists(state_dir)
        subject.delete(state_dir)
        assert not os.path.exists(state_dir)

        # Swallows FileNotFoundError
        subject.delete(filepath)
        subject.delete(state_dir)

    def test_clear(
        self,
        subject: LocalFilesystemStateStoreManager,
        state_path,
        state_ids_with_expected_states,
    ):
        for (state_id, expected_state) in state_ids_with_expected_states:
            state_dir = os.path.join(state_path, encode_if_on_windows(state_id))
            Path(state_dir).mkdir(parents=True)
            with open(os.path.join(state_dir, "state.json"), "w+") as state_file:
                json.dump(expected_state, state_file)
        for (state_id, _) in state_ids_with_expected_states:
            state_dir = os.path.join(state_path, encode_if_on_windows(state_id))
            filepath = os.path.join(state_dir, "state.json")
            assert os.path.exists(filepath)
            subject.clear(state_id)
            assert not os.path.exists(os.path.dirname(filepath))


class TestAZStorageStateStoreManager:
    @pytest.fixture(scope="function")
    def subject(self, function_scoped_test_dir):
        return AZStorageStateStoreManager(
            uri="azure://meltano/state/",
            connection_string="testing_connection_string",
            lock_timeout_seconds=10,
        )

    @pytest.fixture(scope="function")
    def mock_client(self):
        with patch(
            "azure.storage.blob.BlobServiceClient",
        ) as mock_client:
            yield mock_client

    def test_client(self, subject: AZStorageStateStoreManager, mock_client):
        # Call twice to assure memoization
        _ = subject.client  # noqa: F541 WPS122
        _ = subject.client  # noqa: F541 WPS122
        mock_client.from_connection_string.assert_called_once_with(
            "testing_connection_string"
        )

    def test_is_file_not_found_error_true(
        self, subject: AZStorageStateStoreManager, mock_client
    ):
        got_reader = False
        mock_container_client = MagicMock()
        mock_container_client.container_name = subject.container_name
        subject.client.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.side_effect = ResourceNotFoundError(
            "Operation returned an invalid status 'The specified blob does not exist.'\nErrorCode:BlobNotFound"
        )
        try:
            with subject.get_reader("nonexistent"):
                got_reader = True
        except Exception as e:
            assert subject.is_file_not_found_error(e)
        assert not got_reader

    def test_is_file_not_found_error_false(
        self, subject: AZStorageStateStoreManager, mock_client
    ):
        got_reader = False
        mock_container_client = MagicMock()
        mock_container_client.container_name = subject.container_name
        subject.client.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.side_effect = ResourceNotFoundError(
            "Operation returned an invalid status 'The specified container does not exist.'\nErrorCode:ContainerNotFound"
        )
        try:
            with subject.get_reader("nonexistent"):
                got_reader = True
        except Exception as e:
            assert not subject.is_file_not_found_error(e)
        assert not got_reader

    def test_state_path(self, subject: AZStorageStateStoreManager):
        assert subject.state_dir == "state"

    def test_delete(self, subject, mock_client):
        mock_blob_client = MagicMock()
        subject.client.get_blob_client.return_value = mock_blob_client
        subject.delete("some_path")
        mock_blob_client.delete_blob.assert_called_once()

    def test_get_state_ids(self, subject, mock_client):
        mock_container_client = MagicMock()
        mock_container_client.list_blobs.return_value = (
            BlobProperties(name=f"state/state_id_{i}/state.json") for i in range(10)
        )
        subject.client.get_container_client.return_value = mock_container_client
        assert set(subject.get_state_ids()) == {f"state_id_{i}" for i in range(10)}
        mock_container_client.list_blobs.assert_called_once_with(
            name_starts_with="state/"
        )


class TestS3StateStoreManager:
    @contextmanager
    def stubber(self) -> Iterator[Stubber]:
        with patch(
            "meltano.core.state_store.S3StateStoreManager.client",
            new_callable=PropertyMock,
        ) as mock_client:
            mock_client.return_value = client("s3")
            with Stubber(mock_client.return_value) as stubber:
                yield stubber

    @pytest.fixture
    def subject(self, function_scoped_test_dir):
        return S3StateStoreManager(
            uri="s3://test_access_key_id:test_secret_access_key@meltano/state",
            container_name="testing",
            lock_timeout_seconds=10,
        )

    def test_is_file_not_found_error_true(self, subject: S3StateStoreManager):
        got_reader = False
        with self.stubber() as stubber:
            stubber.add_client_error("get_object", service_error_code="NoSuchKey")
            try:
                with subject.get_reader("does_not_exist"):
                    got_reader = True
            except Exception as e:
                assert subject.is_file_not_found_error(e)
        assert not got_reader

    def test_is_file_not_found_error_false(self, subject: S3StateStoreManager):
        got_reader = False
        with self.stubber() as stubber:
            stubber.add_client_error("get_object", service_error_code="NoSuchBucket")
            try:
                with subject.get_reader("does_not_exist"):
                    got_reader = True
            except Exception as e:
                assert not subject.is_file_not_found_error(e)
        assert not got_reader

    def test_client_session(self, subject: S3StateStoreManager):
        with patch("boto3.Session") as mock_session:
            _ = subject.client  # noqa: F541 WPS122
            _ = subject.client  # noqa: F541 WPS122
            mock_session.assert_called_once_with(
                aws_access_key_id=subject.aws_access_key_id,
                aws_secret_access_key=subject.aws_secret_access_key,
            )

    def test_client_client(self, subject: S3StateStoreManager):
        with patch("boto3.Session.client") as mock_client:
            _ = subject.client  # noqa: F541 WPS122
            _ = subject.client  # noqa: F541 WPS122
            mock_client.assert_called_once_with("s3", endpoint_url=subject.endpoint_url)

    def test_state_path(self, subject: S3StateStoreManager):
        assert subject.state_dir == "state"

    def test_delete(self, subject: S3StateStoreManager):
        response = {
            "ResponseMetadata": {
                "RequestId": "test_delete",
                "HostId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "accept-ranges": "bytes",
                    "content-length": "236",
                    "content-security-policy": "block-all-mixed-content",
                    "content-type": "application/xml",
                    "server": "test_delete",
                    "strict-transport-security": "max-age=31536000; includeSubDomains",
                    "vary": "Origin, Accept-Encoding",
                    "x-amz-request-id": "test_delete",
                    "x-content-type-options": "nosniff",
                    "x-xss-protection": "1; mode=block",
                    "date": "Mon, 24 Oct 2022 01:05:07 GMT",
                },
                "RetryAttempts": 0,
            },
            "Deleted": [
                {"Key": "/state/test_delete"},
            ],
        }
        with self.stubber() as stubber:
            stubber.add_response(
                "delete_objects",
                response,
                expected_params={
                    "Bucket": subject.bucket,
                    "Delete": {"Objects": [{"Key": "/state/test_delete"}]},
                },
            )
            subject.delete("/state/test_delete")

    def test_get_state_ids(self, subject: S3StateStoreManager):
        response = {
            "ResponseMetadata": {
                "RequestId": "test_get_state_ids",
                "HostId": "",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "accept-ranges": "bytes",
                    "content-length": "993",
                    "content-security-policy": "block-all-mixed-content",
                    "content-type": "application/xml",
                    "server": "test_get_state_ids",
                    "strict-transport-security": "max-age=31536000; includeSubDomains",
                    "vary": "Origin, Accept-Encoding",
                    "x-amz-request-id": "test_get_state_ids",
                    "x-content-type-options": "nosniff",
                    "x-xss-protection": "1; mode=block",
                    "date": "Wed, 26 Oct 2022 01:15:33 GMT",
                },
                "RetryAttempts": 0,
            },
            "IsTruncated": False,
            "Contents": [
                {
                    "Key": "state/state_id_2/state.json",
                    "LastModified": datetime.datetime(
                        2022, 10, 26, 1, 15, 26, 173000, tzinfo=tzutc()
                    ),
                    "ETag": '"test_get_state_ids"',
                    "Size": 60,
                    "StorageClass": "STANDARD",
                    "Owner": {
                        "DisplayName": "test_get_state_ids",
                        "ID": "test_get_state_ids",
                    },
                },
                {
                    "Key": "state/state_id_1/state.json",
                    "LastModified": datetime.datetime(
                        2022, 10, 24, 1, 15, 12, 450000, tzinfo=tzutc()
                    ),
                    "ETag": '"test_get_state_ids"',
                    "Size": 60,
                    "StorageClass": "STANDARD",
                    "Owner": {
                        "DisplayName": "test_get_state_ids",
                        "ID": "test_get_state_ids",
                    },
                },
            ],
            "Name": subject.bucket,
            "Prefix": subject.prefix,
            "Delimiter": "",
            "MaxKeys": 1000,
            "EncodingType": "url",
            "KeyCount": 2,
        }
        with self.stubber() as stubber:
            stubber.add_response(
                "list_objects_v2",
                response,
                expected_params={"Bucket": subject.bucket, "Prefix": subject.prefix},
            )
            assert set(subject.get_state_ids()) == {"state_id_1", "state_id_2"}


class TestGCSStateStoreManager:
    @pytest.fixture(scope="function")
    def subject(self, function_scoped_test_dir):
        return GCSStateStoreManager(
            uri="gs://meltano/state/",
            application_credentials="path/to/creds/file",
            lock_timeout_seconds=10,
        )

    @pytest.fixture(scope="function")
    def mock_client(self):
        with patch(
            "google.cloud.storage.Client",
        ) as mock_client:
            yield mock_client

    def test_client(self, subject: GCSStateStoreManager, mock_client):
        # Call twice to assure memoization
        _ = subject.client  # noqa: F541 WPS122
        _ = subject.client  # noqa: F541 WPS122
        mock_client.from_service_account_json.assert_called_once_with(
            subject.application_credentials
        )

    def test_is_file_not_found_error_true(
        self, subject: GCSStateStoreManager, mock_client
    ):
        got_reader = False
        mock_bucket = MagicMock()
        mock_bucket.get_blob.return_value = None
        subject.client.bucket.return_value = mock_bucket
        try:
            with subject.get_reader("nonexistent"):
                got_reader = True
        except Exception as e:
            assert subject.is_file_not_found_error(e)
        assert not got_reader

    def test_is_file_not_found_error_false(
        self, subject: GCSStateStoreManager, mock_client
    ):
        got_reader = False
        mock_bucket = MagicMock()
        mock_bucket.get_blob.side_effect = ValueError("Some other error")
        subject.client.bucket.return_value = mock_bucket
        try:
            with subject.get_reader("nonexistent"):
                got_reader = True
        except Exception as e:
            assert not subject.is_file_not_found_error(e)
        assert not got_reader

    def test_state_path(self, subject: GCSStateStoreManager):
        assert subject.state_dir == "state"

    def test_delete(self, subject: GCSStateStoreManager, mock_client):
        mock_blob = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        subject.client.bucket.return_value = mock_bucket
        subject.delete("some_path")
        mock_blob.delete.assert_called_once()

    def test_get_state_ids(self, subject: GCSStateStoreManager, mock_client):
        subject.client.list_blobs.return_value = (
            Blob(bucket=Bucket("meltano"), name=f"state/state_id_{i}/state.json")
            for i in range(10)
        )
        assert set(subject.get_state_ids()) == {f"state_id_{i}" for i in range(10)}
        subject.client.list_blobs.assert_called_once_with(bucket_or_name="meltano")
