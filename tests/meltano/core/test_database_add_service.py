import pytest
import yaml
import os
import shutil

from meltano.core.database_add_service import DatabaseAddService


class TestDatabaseAddService:
    @pytest.fixture
    def subject(self, project):
        database_service = DatabaseAddService(project)
        assert database_service

        return database_service

    def test_add_database_should_update_file(self, subject):
        name = "sample %% name ^^ 123"
        subject.add(
            name=name,
            host="127.0.0.1",
            database="sample_database",
            schema="analytics",
            username="jeffery",
            password="freedomforjeffery",
        )

        root_name = subject.environmentalize(name)
        assert yaml.load(
            open(f".meltano/.database_{root_name.lower()}.yml").read()
        ) == {
            "database": "sample_database",
            "host": "127.0.0.1",
            "name": "sample_name_123",
            "password": "freedomforjeffery",
            "root_name": "SAMPLE_NAME_123",
            "schema": "analytics",
            "username": "jeffery",
        }
