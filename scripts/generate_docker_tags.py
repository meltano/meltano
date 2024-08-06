#!/usr/bin/env python3

"""Script to generate docker tags for Meltano images.

Usage:

python scripts/generate_docker_tags.py \
    --git-sha e4bdaedab02462e9e19a1bf063cbce26bc3c7581 \
    -v 3.0.0rc0 \
    -p 3.9 \
    -d 3.9 \
    -r docker.io
"""

from __future__ import annotations

import argparse

from packaging.version import Version


def main() -> None:
    """Generate docker tags for the given package version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--registry", default="docker.io")
    parser.add_argument("-v", "--package-version", required=True)
    parser.add_argument("-p", "--python-version", required=True)
    parser.add_argument("-d", "--default-python", required=True)
    parser.add_argument("--git-sha")
    args = parser.parse_args()

    is_default_python = args.default_python == args.python_version
    version = Version(args.package_version)
    tags = []

    # To save space, only publish the `latest` tag for each
    # images to the GitHub registry
    if args.registry != "ghcr.io":
        tags.append(f"v{version}-python{args.python_version}")

        if not version.is_prerelease:
            tags.extend(
                (
                    f"v{version.major}-python{args.python_version}",
                    f"v{version.major}.{version.minor}-python{args.python_version}",
                ),
            )
            if is_default_python:
                tags.extend(
                    (
                        f"SHA-{args.git_sha}",
                        f"v{version.major}",
                        f"v{version.major}.{version.minor}",
                        f"v{version}",
                    ),
                )

    # ghcr.io: publish `latest` for ALL versions
    # docker.io: only publish `latest` for final releases
    if not version.is_prerelease or args.registry == "ghcr.io":
        tags.append(f"latest-python{args.python_version}")

        if is_default_python:
            tags.append("latest")

    print("\n".join(tags))  # noqa: T201


if __name__ == "__main__":
    main()
