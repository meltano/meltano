import pytest

from meltano.core.permissions.utils.snowflake_grants import SnowflakeGrantsGenerator


@pytest.fixture(scope="class")
def test_grants_to_role():

    roles = {
        "pluthra": {
            "operate": {
                "warehouse": [
                    "analyst_xs"
                ]
            },
            "usage": {
                "warehouse": [
                    "analyst_xs"
                ]
            }
        },
        "boneyard": {
            "usage": {
                "database": [
                    "analytics"
                ],
                "schema": [
                    "analytics.boneyard"
                ],
                "warehouse": [
                    "analyst_xs"
                ]
            },
            "select": {
                "table": [
                    "analytics.boneyard.interviews",
                    "analytics.boneyard.rubric_max_points",
                    "analytics.boneyard.testing",
                    "analytics.boneyard.test_sheet"
                ]
            },
            "operate": {
                "warehouse": [
                    "analyst_xs"
                ]
            }
        },
        "analyst_people": {
            "usage": {
                "role": [
                    "bamboohr",
                    "boneyard",
                    "greenhouse"
                ]
            }
        }
    }

    return roles

@pytest.fixture(scope="class")
def test_roles_granted_to_user():
    return {
        "pluthra": [
            "analyst_people",
            "pluthra"
        ]
    }

class TestSnowflakeGrants:
    def test_generate_grant_roles(self, test_grants_to_role, test_roles_granted_to_user):
        generator = SnowflakeGrantsGenerator(test_grants_to_role, test_roles_granted_to_user)

        user_config = {
            "pluthra": {
                "can_login": True,
                "member_of": [
                    "boneyard",
                    "pluthra"
                ]
            }
        }

        role_command_list = generator.generate_grant_roles(
            "roles", "pluthra", user_config["pluthra"]
        )

        role_lower_list = [cmd.get("sql", "").lower() for cmd in role_command_list]

        user_command_list = generator.generate_grant_roles(
            "users", "pluthra", user_config["pluthra"]
        )

        user_lower_list = [cmd.get("sql", "").lower() for cmd in user_command_list]

        assert "grant role boneyard to user pluthra" in user_lower_list
        assert "grant role pluthra to user pluthra" in user_lower_list
        assert "revoke role analyst_people from user pluthra" in user_lower_list
