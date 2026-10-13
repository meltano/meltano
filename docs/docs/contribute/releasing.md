---
title: Release Process
description: How Meltano maintainers cut a new release.
layout: doc
sidebar_position: 5
sidebar_class_name: hidden
---

Releases are driven by two GitHub Actions workflows: [`version_bump.yml`](https://github.com/meltano/meltano/blob/main/.github/workflows/version_bump.yml) prepares the release, and [`build.yml`](https://github.com/meltano/meltano/blob/main/.github/workflows/build.yml) publishes it once the GitHub release is published.

Only maintainers with permission to run workflows and publish releases on the repository can cut a release.

## Versioning

Meltano follows [semantic versioning](https://semver.org/). Versions are managed by [commitizen](https://commitizen-tools.github.io/commitizen/), configured in the `[tool.commitizen]` section of `pyproject.toml`, and tags have the format `vMAJOR.MINOR.PATCH` (with a prerelease suffix for pre-releases).

The changelog and the automatic version increment are derived from the titles of merged pull requests, so they must follow the [conventional commit](./merge.md#semantic-prs) syntax.

The following files are updated with the new version:

- `pyproject.toml`
- `docs/package.json`
- `.github/ISSUE_TEMPLATE/bug.yml`

## Cutting a release

1. Make sure `main` is green and contains everything you want in the release.
1. Run the [**Version bump**](https://github.com/meltano/meltano/actions/workflows/version_bump.yml) workflow from `main` with the following inputs:
   - **bump**: `auto` (default, inferred from commit types), or force `patch`, `minor` or `major`.
   - **prerelease**: `none` for a stable release, or `alpha`, `beta` or `rc` for a pre-release.
1. The workflow bumps the version, refreshes `uv.lock` and `docs/package-lock.json`, and opens a pull request titled `chore: Release vX.Y.Z` from the `release/vX.Y.Z` branch, labeled `release`. For stable releases it also creates a **draft** GitHub release with the changelog fragment as its body.
1. Review the pull request, in particular the generated changelog, and merge it.
1. Review the draft release notes on the [releases page](https://github.com/meltano/meltano/releases), edit them if needed, and **publish** the release.
1. Publishing the release triggers `build.yml`, which:
   - checks that the release tag matches the package version in `pyproject.toml`,
   - builds the wheel and sdist,
   - builds and pushes the Docker images to Docker Hub, and
   - publishes the package to [PyPI](https://pypi.org/project/meltano/) through trusted publishing, in the `publishing` environment.
1. Verify that the new version is available on PyPI and Docker Hub.

## Pre-releases

Pre-releases (`alpha`, `beta`, `rc`) skip changelog generation and do not create a draft GitHub release. Create the release manually from the release tag if one is needed, and mark it as a pre-release so it is not picked as the `latest` Docker tag.

## Docker image refresh

`build.yml` also runs weekly (Sundays at 04:45 UTC) and rebuilds and pushes the Docker images for the latest stable release, so they pick up base image and OS security updates. It does not publish to PyPI.

## Troubleshooting

**`Release tag ('vX') and package version ('vY') do not match!`**
: The release was published from a tag that doesn't match `pyproject.toml`. Make sure the release pull request was merged before publishing the release, and that the draft release tag is `v` followed by the version in `pyproject.toml`.
