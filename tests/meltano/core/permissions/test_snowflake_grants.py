import pytest

from meltano.core.permissions.utils.snowflake_grants import SnowflakeGrantsGenerator


@pytest.fixture(scope="class")
def test_grants_to_role():

    roles = {
        "functional_role": {
            "usage": {
                "role": [
                    "object_role_1",
                    "object_role_2",
                ]
            }
        }
    }

    return roles

@pytest.fixture(scope="class")
def test_roles_granted_to_user():
    return {
        "user_name": [
            "function_role",
            "user_role"
        ]
    }

class TestSnowflakeGrants:
    def test_generate_grant_roles(self, test_grants_to_role, test_roles_granted_to_user):
        generator = SnowflakeGrantsGenerator(test_grants_to_role, test_roles_granted_to_user)

        user_config = {
            "user_name": {
                "can_login": True,
                "member_of": [
                    "object_role",
                    "user_role"
                ]
            }
        }

        role_config = {
            "functional_role": {
                "warehouses": ["warehouse_1"],
                "member_of": [
                    "object_role_2",
                    "object_role_3"
                ]
            }
        }

        role_command_list = generator.generate_grant_roles(
            "roles", "functional_role", role_config["functional_role"]
        )

        role_lower_list = [cmd.get("sql", "").lower() for cmd in role_command_list]

        assert "grant role object_role_2 to role functional_role" in role_lower_list
        assert "grant role object_role_3 to role functional_role" in role_lower_list
        assert "revoke role object_role_1 from role functional_role" in role_lower_list


        user_command_list = generator.generate_grant_roles(
            "users", "user_name", user_config["user_name"]
        )

        user_lower_list = [cmd.get("sql", "").lower() for cmd in user_command_list]

        assert "grant role object_role to user user_name" in user_lower_list
        assert "grant role user_role to user user_name" in user_lower_list
        assert "revoke role function_role from user user_name" in user_lower_list
