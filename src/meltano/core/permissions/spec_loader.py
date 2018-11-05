from typing import List

from .pg_spec_loader import PGSpecLoader
from .error import SpecLoadingError

def grant_permissions(db: str, spec_path: str, dry_run: bool) -> List[str]:
    if db == "postgres":
        spec_loader = PGSpecLoader(spec_path)
    else:
        raise SpecLoadingError(f"Permissions Spec File for {db} is not supported.")

    sql_commands = spec_loader.generate_sql_commands()

    # just check at the moment
    # if not dry_run:
    #     # Do something

    # Always return the SQL commands that [would] run
    return sql_commands
