from typing import List

from meltano.core.permissions.pg_spec_loader import PGSpecLoader
from meltano.core.permissions.snowflake_spec_loader import SnowflakeSpecLoader
from meltano.core.permissions.utils.error import SpecLoadingError
from meltano.core.permissions.utils.snowflake_connector import SnowflakeConnector


def grant_permissions(db: str, spec_path: str, dry_run: bool) -> List[str]:
    if db == "postgres":
        spec_loader = PGSpecLoader(spec_path)
    elif db == "snowflake":
        spec_loader = SnowflakeSpecLoader(spec_path)
    else:
        raise SpecLoadingError(f"Permissions Spec File for {db} is not supported.")

    sql_grant_queries = spec_loader.generate_permission_queries()

    run_queries = []

    if not dry_run:
        conn = SnowflakeConnector()
        for query in sql_grant_queries:
            status = None
            if not query.get("already_granted"):
                try:
                    result = conn.run_query(query.get("sql"))
                    outcome = result.fetchall()
                    status = True
                except:
                    status = False

                ran_query = query
                ran_query["run_status"] = status
                run_queries.append(ran_query)
    else:
        run_queries = sql_grant_queries

    # Always return the SQL commands that ran
    return run_queries
