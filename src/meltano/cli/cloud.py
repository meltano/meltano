"""Meltano Cloud CLI.

The Meltano Cloud CLI is implemented as a subproject that can be installed and
used separately, but is also bundled with Meltano.
"""

from __future__ import annotations

from meltano.cli.cli import cli
from meltano.cloud.cli import cloud  # noqa: F401

cli.add_command(cloud)
