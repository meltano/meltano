import io

from meltano.common.manifest import *
from meltano.common.manifest_reader import *
from meltano.common.manifest_writer import *


SAMPLE = """
version: '1.0'
person:
  attributes:
  - alias: product_id
    input:
      name: Product ID
      type: string
    output:
      name: product_id
      type: string
    metadata:
      is_pkey: False
"""

def test_reader():
    reader = ManifestReader("sample")
    manifest = reader.loads(SAMPLE)

    assert(manifest.version == "1.0")
    assert(len(manifest.entities) == 1)


def test_writer():
    manifest = ManifestReader("sample").loads(SAMPLE)
    buf = io.StringIO()
    writer = ManifestWriter(buf)
    writer.write(manifest)

    round_trip = ManifestReader("sample").loads(buf.getvalue())

    assert(manifest.version == round_trip.version)
    for a, b in zip(manifest.entities, round_trip.entities):
        assert(a.alias == b.alias)
