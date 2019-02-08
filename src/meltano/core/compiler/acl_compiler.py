import json
from typing import Iterator, Union, Dict
from pathlib import Path
from functools import reduce
from pyhocon import ConfigFactory

from meltano.core.utils import nest


PathBasis = Union[str, Path]


class ACLCompiler:
    VERSION = "1.0"
    OUTPUT_NAME = "acls.m5oc"

    def __init__(self, sources_dir: PathBasis, output_dir: PathBasis):
        self.sources_dir = Path(sources_dir)
        self.output_path = Path(output_dir, self.OUTPUT_NAME)

    def sources(self) -> Iterator[Path]:
        return self.sources_dir.glob("*acls.m5o")

    def parse(self, input: PathBasis) -> Dict:
        """Parse single file to its compiled representation."""
        raw = ConfigFactory.parse_file(input)

        # the raw definition is easy to write, edit and version
        # the compiled representation should be easy to use
        compiled = {
            "version": self.VERSION,
            "acl": {"view": {}, "create": {}, "delete": {}},
            "roles": {},
        }

        # start at the `roles` definition
        for role, role_def in raw.get("roles", {}).items():
            compiled["roles"][role] = role_def["users"]

            # un-nest the whole ACL declaration into
            # perm: view | create | delete
            # target: designs | reports | dashboards
            # declaration: name of the shown entity | * (for all)
            acls = (
                (perm, target, declaration)
                for perm, acl_def in role_def.get("acl", {}).items()
                for target, declarations in acl_def.items()
                for declaration in declarations
            )

            for perm, target, declaration in acls:
                # _default will be treated as the fallback for
                # the whole target/acl
                declaration = "_default" if declaration == "*" else declaration

                roles = nest(compiled, f"acl.{perm}.{target}")

                if declaration in roles:
                    roles[declaration].append(role)
                else:
                    roles[declaration] = [role]

        return compiled

    def assemble(self, parsed):
        # this specific compiler has a single source file
        return next(parsed)

    def compile(self):
        """Parse all files and write the compiled output."""

        compiled = (self.parse(input) for input in self.sources())
        assembled = self.assemble(compiled)

        with self.output_path.open("w") as out:
            json.dump(assembled, out, indent=2)
