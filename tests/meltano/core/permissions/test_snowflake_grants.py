import pytest

from meltano.core.permissions.utils.snowflake_grants import SnowflakeGrantsGenerator


@pytest.fixture(scope="class")
def test_database_config():
    config = {
        "databases": {
            "database_1": {"shared": False},
            "database_2": {"shared": False},
            "database_3": {"shared": False},
            "shared_database_1": {"shared": True},
            "shared_database_2": {"shared": True},
        }
    }

    return config


@pytest.fixture(scope="class")
def test_shared_dbs(test_database_config):
    shared_dbs = []
    databases = test_database_config.get("databases", {})
    for database in databases:
        if databases.get(database, {}).get("shared", False):
            shared_dbs.append(database)

    return shared_dbs


@pytest.fixture(scope="class")
def test_role_config():
    config = {
        "functional_role": {
            "warehouses": ["warehouse_2", "warehouse_3"],
            "member_of": ["object_role_2", "object_role_3"],
            "privileges": {
                "databases": {
                    "read": ["database_2", "shared_database_2"],
                    "write": ["database_3"],
                }
            },
        }
    }

    return config


@pytest.fixture(scope="class")
def test_user_config():
    config = {
        "user_name": {"can_login": True, "member_of": ["object_role", "user_role"]}
    }

    return config


@pytest.fixture(scope="class")
def test_grants_to_role():
    roles = {
        "functional_role": {
            "usage": {
                "database": ["database_1", "database_2", "shared_database_1"],
                "role": ["object_role_1", "object_role_2"],
                "warehouse": ["warehouse_1", "warehouse_2"],
            },
            "operate": {"warehouse": ["warehouse_1", "warehouse_2"]},
            "monitor": {"database": ["database_1", "database_2"]},
            "create schema": {"database": ["database_1", "database_2"]},
        }
    }

    return roles


@pytest.fixture(scope="class")
def test_roles_granted_to_user():
    config = {"user_name": ["function_role", "user_role"]}

    return config


class TestSnowflakeGrants:
    def test_generate_grant_roles(
        self,
        test_grants_to_role,
        test_roles_granted_to_user,
        test_role_config,
        test_user_config,
    ):
        generator = SnowflakeGrantsGenerator(
            test_grants_to_role, test_roles_granted_to_user
        )

        role_command_list = generator.generate_grant_roles(
            "roles", "functional_role", test_role_config["functional_role"]
        )

        role_lower_list = [cmd.get("sql", "").lower() for cmd in role_command_list]

        assert "grant role object_role_2 to role functional_role" in role_lower_list
        assert "grant role object_role_3 to role functional_role" in role_lower_list
        assert "revoke role object_role_1 from role functional_role" in role_lower_list

        user_command_list = generator.generate_grant_roles(
            "users", "user_name", test_user_config["user_name"]
        )

        user_lower_list = [cmd.get("sql", "").lower() for cmd in user_command_list]

        assert "grant role object_role to user user_name" in user_lower_list
        assert "grant role user_role to user user_name" in user_lower_list
        assert "revoke role function_role from user user_name" in user_lower_list

    def test_generate_warehouse_grants(
        self,
        test_grants_to_role,
        test_roles_granted_to_user,
        test_role_config,
        test_user_config,
    ):
        generator = SnowflakeGrantsGenerator(
            test_grants_to_role, test_roles_granted_to_user
        )

        warehouse_command_list = generator.generate_warehouse_grants(
            "functional_role", test_role_config["functional_role"]["warehouses"]
        )

        warehouse_lower_list = [
            cmd.get("sql", "").lower() for cmd in warehouse_command_list
        ]

        assert (
            "grant usage on warehouse warehouse_2 to role functional_role"
            in warehouse_lower_list
        )
        assert (
            "grant usage on warehouse warehouse_3 to role functional_role"
            in warehouse_lower_list
        )
        assert (
            "revoke usage on warehouse warehouse_1 from role functional_role"
            in warehouse_lower_list
        )

        assert (
            "grant operate on warehouse warehouse_2 to role functional_role"
            in warehouse_lower_list
        )
        assert (
            "grant operate on warehouse warehouse_3 to role functional_role"
            in warehouse_lower_list
        )
        assert (
            "revoke operate on warehouse warehouse_1 from role functional_role"
            in warehouse_lower_list
        )

    def test_generate_database_grants(
        self,
        test_grants_to_role,
        test_roles_granted_to_user,
        test_role_config,
        test_user_config,
        test_shared_dbs,
    ):
        generator = SnowflakeGrantsGenerator(
            test_grants_to_role, test_roles_granted_to_user
        )

        database_command_list = generator.generate_database_grants(
            "functional_role",
            test_role_config["functional_role"]["privileges"]["databases"],
            test_shared_dbs,
        )

        database_lower_list = [
            cmd.get("sql", "").lower() for cmd in database_command_list
        ]
        print(database_lower_list)

        assert (
            "grant usage on database database_2 to role functional_role"
            in database_lower_list
        )
        assert (
            "grant usage, monitor, create schema on database database_3 to role functional_role"
            in database_lower_list
        )
        assert (
            "revoke usage on database database_1 from role functional_role"
            in database_lower_list
        )
        assert (
            "revoke monitor, create schema on database database_1 from role functional_role"
            in database_lower_list
        )
        assert (
            "revoke monitor, create schema on database database_2 from role functional_role"
            in database_lower_list
        )

        # Shared DBs
        assert (
            "grant imported privileges on database shared_database_2 to role functional_role"
            in database_lower_list
        )
        assert (
            "revoke imported privileges on database shared_database_1 from role functional_role"
            in database_lower_list
        )
