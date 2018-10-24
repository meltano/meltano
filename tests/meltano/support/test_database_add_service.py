import pytest
import yaml
import os
import shutil

from meltano.support.database_add_service import DatabaseAddService


class TestDatabaseAddService:
    def test_default_init_should_not_fail(self):
        database_service = DatabaseAddService()
        assert database_service

    def test_add_database_should_update_file(self):
        os.mkdir("./.meltano")
        database_service = DatabaseAddService()
        name = "sample %% name ^^ 123"
        database_service.add(
            name=name,
            host="127.0.0.1",
            database="sample_database",
            schema="analytics",
            username="jeffery",
            password="freedomforjeffery",
        )

        root_name = database_service.environmentalize(name)
        assert yaml.load(
            open(f"./.meltano/.database_{root_name.lower()}.yml").read()
        ) == {
            "database": "sample_database",
            "host": "127.0.0.1",
            "name": "sample_name_123",
            "password": "freedomforjeffery",
            "root_name": "SAMPLE_NAME_123",
            "schema": "analytics",
            "username": "jeffery",
        }
        shutil.rmtree("./.meltano")
