from __future__ import annotations

import datetime
import json
import typing as t
from contextlib import contextmanager
from unittest.mock import PropertyMock, patch

import botocore.exceptions
import moto
import pytest
from boto3 import client
from botocore.stub import Stubber

from meltano.core.state_store import MeltanoState
from meltano.core.state_store.s3.backend import S3StateStoreManager

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    import faker


class TestS3StateStoreManager:
    @contextmanager
    def stubber(self) -> Iterator[Stubber]:
        with patch(
            "meltano.core.state_store.s3.backend.S3StateStoreManager.client",
            new_callable=PropertyMock,
        ) as mock_client:
            mock_client.return_value = client("s3")
            with Stubber(mock_client.return_value) as stubber:
                yield stubber

    @pytest.fixture
    def subject(self):
        return S3StateStoreManager(
            uri="s3://test_access_key_id:test_secret_access_key@meltano/state",
            container_name="testing",
            lock_timeout_seconds=10,
        )

    def test_is_file_not_found_error_true(self, subject: S3StateStoreManager) -> None:
        with self.stubber() as stubber:
            stubber.add_client_error("get_object", service_error_code="NoSuchKey")
            assert subject.get("does_not_exist") is None

    def test_is_file_not_found_error_false(self, subject: S3StateStoreManager) -> None:
        with self.stubber() as stubber:
            stubber.add_client_error("get_object", service_error_code="NoSuchBucket")
            with pytest.raises(botocore.exceptions.ClientError) as exc_info:
                subject.get("does_not_exist")

            assert isinstance(exc_info.value, botocore.exceptions.ClientError)
            assert exc_info.value.response["Error"]["Code"] == "NoSuchBucket"

    def test_client_session(self, subject: S3StateStoreManager) -> None:
        with patch("boto3.Session") as mock_session:
            _ = subject.client
            _ = subject.client
            mock_session.assert_called_once_with(
                aws_access_key_id=subject.aws_access_key_id,
                aws_secret_access_key=subject.aws_secret_access_key,
            )

    def test_client_client(self, subject: S3StateStoreManager) -> None:
        with patch("boto3.Session.client") as mock_client:
            _ = subject.client
            _ = subject.client
            mock_client.assert_called_once_with("s3", endpoint_url=subject.endpoint_url)

    def test_state_path(self, subject: S3StateStoreManager) -> None:
        assert subject.state_dir == "state"

    def test_set_first_time(
        self,
        monkeypatch: pytest.MonkeyPatch,
        faker: faker.Faker,
    ) -> None:
        monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
        monkeypatch.delenv("AWS_PROFILE", raising=False)
        state_id = faker.pystr()
        with moto.mock_aws():
            store_manager = S3StateStoreManager(
                uri="s3://test_access_key_id:test_secret_access_key@meltano/state",
                lock_timeout_seconds=10,
            )
            store_manager.client.create_bucket(Bucket=store_manager.bucket)
            store_manager.set(MeltanoState(state_id=state_id, completed_state={}))

    def test_update_fail_object_in_glacier(
        self,
        monkeypatch: pytest.MonkeyPatch,
        faker: faker.Faker,
    ) -> None:
        monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
        monkeypatch.delenv("AWS_PROFILE", raising=False)
        state_id = faker.pystr()
        with moto.mock_aws():
            store_manager = S3StateStoreManager(
                uri="s3://test_access_key_id:test_secret_access_key@meltano/state",
                lock_timeout_seconds=10,
            )
            store_manager.client.create_bucket(Bucket=store_manager.bucket)
            store_manager.client.put_object(
                Bucket=store_manager.bucket,
                Key=f"state/{state_id}/state.json",
                Body=json.dumps({}).encode(),
                StorageClass="GLACIER",
            )
            with pytest.raises(OSError, match="unable to access") as exc_info:
                store_manager.update(
                    MeltanoState(
                        state_id=state_id,
                        completed_state={},
                    ),
                )

            exc = exc_info.value
            assert isinstance(exc.__cause__, botocore.exceptions.ClientError)
            assert exc.__cause__.response["Error"]["Code"] == "InvalidObjectState"

    def test_update_fail_bucket_does_not_exist(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
        monkeypatch.delenv("AWS_PROFILE", raising=False)
        with moto.mock_aws():
            store_manager = S3StateStoreManager(
                uri="s3://test_access_key_id:test_secret_access_key@meltano/state",
                lock_timeout_seconds=10,
            )
            with pytest.raises(botocore.exceptions.ClientError) as exc_info:
                store_manager.update(
                    MeltanoState(
                        state_id="state-id",
                        completed_state={},
                    ),
                )

            assert isinstance(exc_info.value, botocore.exceptions.ClientError)
            assert exc_info.value.response["Error"]["Code"] == "NoSuchBucket"

    def test_delete(self, subject: S3StateStoreManager) -> None:
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
            subject.delete_file("/state/test_delete")

    def test_get_state_ids(self, subject: S3StateStoreManager) -> None:
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
                        2022,
                        10,
                        26,
                        1,
                        15,
                        26,
                        173000,
                        tzinfo=datetime.timezone.utc,
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
                        2022,
                        10,
                        24,
                        1,
                        15,
                        12,
                        450000,
                        tzinfo=datetime.timezone.utc,
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
                    "Key": "state.json",
                    "LastModified": datetime.datetime(
                        2022,
                        10,
                        24,
                        1,
                        15,
                        12,
                        450000,
                        tzinfo=datetime.timezone.utc,
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
            "Delimiter": "",
            "MaxKeys": 1000,
            "EncodingType": "url",
            "KeyCount": 2,
        }
        with self.stubber() as stubber:
            stubber.add_response(
                "list_objects_v2",
                response,
                expected_params={"Bucket": subject.bucket, "Prefix": "/state"},
            )
            assert set(subject.get_state_ids()) == {"state_id_1", "state_id_2"}
