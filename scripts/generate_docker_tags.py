#!/usr/bin/env python3

"""Script to generate docker tags for Meltano images.

Usage:

python scripts/generate_docker_tags.py \
    --git-sha e4bdaedab02462e9e19a1bf063cbce26bc3c7581 \
    --package-version 3.0.0rc0 \
    --python-version 3.10 \
    --default-python 3.10 \
    --registry docker.io
"""

from __future__ import annotations

import argparse
import os

from packaging.version import Version


def main() -> None:
    """Generate docker tags for the given package version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--registry", default="docker.io")
    parser.add_argument("-v", "--package-version", required=True)
    parser.add_argument("-p", "--python-version", required=True)
    parser.add_argument("-d", "--default-python", required=True)
    parser.add_argument("--git-sha")
    parser.add_argument(
        "--slim",
        action="store_true",
        help="Generate tags for slim images",
    )
    parser.add_argument(
        "--latest-version",
        default=None,
        help=(
            "The current latest published version. When provided and the registry is "
            "not 'ghcr.io', 'latest' tags are only generated if --package-version >= "
            "--latest-version. This prevents backport releases from overwriting the "
            "'latest' tag with an older version."
        ),
    )
    args = parser.parse_args()

    is_default_python = args.default_python == args.python_version
    version = Version(args.package_version)
    tags = []

    # Add suffix for slim images
    slim = args.slim or os.getenv("DOCKER_TAGS_SLIM") == "1"
    suffix = "-slim" if slim else ""

    # For non-ghcr.io registries, only apply 'latest' if this version is >=
    # the current latest published version. This prevents backport releases
    # (e.g. v3.9.2 published after v4.1.2) from overwriting 'latest'.
    is_overall_latest = (
        args.latest_version is None
        or args.registry == "ghcr.io"
        or version >= Version(args.latest_version)
    )

    # To save space, only publish the `latest` tag for each
    # images to the GitHub registry
    if args.registry != "ghcr.io":
        tags.append(f"v{version}-python{args.python_version}{suffix}")

        if not version.is_prerelease:
            tags.extend(
                (
                    f"v{version.major}-python{args.python_version}{suffix}",
                    f"v{version.major}.{version.minor}-python{args.python_version}{suffix}",
                ),
            )
            if is_default_python:
                tags.extend(
                    (
                        f"SHA-{args.git_sha}{suffix}",
                        f"v{version.major}{suffix}",
                        f"v{version.major}.{version.minor}{suffix}",
                        f"v{version}{suffix}",
                    ),
                )

    # ghcr.io: publish `latest` for ALL versions
    # docker.io: only publish `latest` for final releases that are the overall latest
    if (not version.is_prerelease or args.registry == "ghcr.io") and is_overall_latest:
        tags.append(f"latest-python{args.python_version}{suffix}")

        if is_default_python:
            tags.append(f"latest{suffix}")

    print("\n".join(tags))  # noqa: T201


if __name__ == "__main__":
    main()
