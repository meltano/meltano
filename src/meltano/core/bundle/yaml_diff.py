import sys
from pprint import pprint

import requests
from deepdiff import DeepDiff
from deepdiff.helper import CannotCompare
from ruamel.yaml import YAML

yaml = YAML()

MELTANO_DISCOVERY_URL = "https://gitlab.com/meltano/meltano/-/raw/\
    master/src/meltano/core/bundle/discovery.yml"

resp = requests.get(MELTANO_DISCOVERY_URL)
resp.raise_for_status()
data = resp.content
endpoint_version = yaml.load(data)


with open("discovery.yml", "r") as meltano_file:
    generated_version = yaml.load(meltano_file)


def compare_func(x, y):
    try:
        return x["name"] == y["name"]
    except Exception:
        raise CannotCompare() from None


ddiff = DeepDiff(
    endpoint_version,
    generated_version,
    verbose_level=2,
    get_deep_distance=True,
    cutoff_distance_for_pairs=1,
    cutoff_intersection_for_pairs=1,
    ignore_order=True,
    iterable_compare_func=compare_func,
)

if len(ddiff) == 0:
    print("Generated discovery.yml matches Meltano endpoint discovery.yml")
    sys.exit()
else:
    print("Generated discovery.yml does not match Meltano endpoint discovery.yml")
    pprint(ddiff, indent=2)
    sys.exit(1)
