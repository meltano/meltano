from typing import List

from meltano.core.permissions.pg_spec_loader import PGSpecLoader
from meltano.core.permissions.snowflake_spec_loader import SnowflakeSpecLoader
from meltano.core.permissions.utils.error import SpecLoadingError


def grant_permissions(db: str, spec_path: str, dry_run: bool) -> List[str]:
    if db == "postgres":
        spec_loader = PGSpecLoader(spec_path)
    elif db == "snowflake":
        spec_loader = SnowflakeSpecLoader(spec_path)
    else:
        raise SpecLoadingError(f"Permissions Spec File for {db} is not supported.")

    sql_permission_queries = spec_loader.generate_permission_queries()

    # just check at the moment
    # if not dry_run:
    #     # Do something

    # Always return the SQL commands that [would] run
    return sql_permission_queries
