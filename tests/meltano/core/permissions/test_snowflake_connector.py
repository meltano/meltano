import pytest

from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector


class TestSnowflakeConnector:
    def test_snowflaky(self):

        db1 = "analytics.schema.table"
        db2 = "1234raw.schema.table"
        db3 = '"123-with-quotes".schema.table'
        db4 = "1_db-9-RANDOM.schema.table"

        assert SnowflakeConnector.snowflaky(db1) == "analytics.schema.table"
        assert SnowflakeConnector.snowflaky(db2) == "1234raw.schema.table"
        assert SnowflakeConnector.snowflaky(db3) == '"123-with-quotes".schema.table'
        assert SnowflakeConnector.snowflaky(db4) == '"1_db-9-RANDOM".schema.table'
