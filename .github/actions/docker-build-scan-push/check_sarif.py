"""Check if the provided SARIF file has any violations at or above some severity level."""

import argparse
import json

DEFAULT_SEVERITY_CUTOFF = 4.0

parser = argparse.ArgumentParser()
parser.add_argument(
    "sarif_path",
    help="The path to the SARIF file to be checked.",
)
parser.add_argument(
    "--severity-cutoff",
    help="Violations with a severity >= this value result in an exit code of 1"
    + " - must be a number in the range [0.0, 10.0].",
    type=float,
    default=DEFAULT_SEVERITY_CUTOFF,
)
args = parser.parse_args()

with open(args.sarif_path) as sarif_file:
    sarif_data = json.load(sarif_file)

first_run = sarif_data["runs"][0]
triggered_rules = first_run["tool"]["driver"]["rules"]

exit(  # noqa: WPS421
    any(
        float(rule["properties"]["security-severity"]) >= args.severity_cutoff
        for rule in triggered_rules
    )
)
