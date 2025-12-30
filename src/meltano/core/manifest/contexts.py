"""Use a manifest to establish contexts in which particular configurations are set.

WARNING: This module is currently just here to flesh out an idea for how
         manifests can be used. It is not used anywhere, and may be subject to
         drastic change. Do not rely on its current implementation unless the
         engineering team agrees that this approach is appropriate.
"""

from __future__ import annotations

import os
import typing as t
from contextlib import contextmanager, suppress

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from meltano.core.manifest.manifest import Manifest

_active_manifest: list[Manifest] = []


def _get_active_manifest() -> Manifest:
    try:
        return _active_manifest[-1]
    except IndexError:
        raise Exception("No manifest has been activated") from None  # noqa: EM101, TRY002, TRY003


@contextmanager
def _manifest_context(manifest: Manifest) -> Iterator[None]:
    _active_manifest.append(manifest)
    try:
        yield
    finally:
        _active_manifest.pop()


@contextmanager
def _env_context(env: Mapping[str, str]) -> Iterator[None]:
    unique_keys = env.keys() - os.environ.keys()
    shared_keys = env.keys() & os.environ.keys()
    prev = {k: v for k, v in os.environ.items() if k in shared_keys}
    os.environ.update(env)
    try:
        yield
    finally:
        for key in unique_keys:
            with suppress(KeyError):
                del os.environ[key]
        for key in shared_keys:
            os.environ[key] = prev[key]


@contextmanager
def manifest_context(manifest: Manifest) -> Iterator[None]:
    """Establish a context within which Meltano can run using a given manifest.

    All relevant general (i.e. excluding plugin-specific, schedule-specific,
    etc.) env vars will be set in the process for the duration of this context
    manager.

    Additionally, this context manager establishes an active manifest, which is
    used by all other context managers within this module.

    Args:
        manifest: The manifest for the current project and environment.

    Yields:
        `None`.
    """
    with _manifest_context(manifest), _env_context(manifest.data["env"]):
        yield


@contextmanager
def plugin_context(plugin_name: str) -> Iterator[None]:
    """Establish a context within which a plugin can be run.

    All relevant env vars for the specified plugin will be set in the process
    for the duration of this context manager.

    Args:
        plugin_name: The name of the plugin to be run.

    Raises:
        ValueError: No plugin was found matching the given plugin name within
            the active manifest.

    Yields:
        `None`.
    """
    manifest = _get_active_manifest()

    try:
        plugin = next(
            x
            for v in manifest.data["plugins"].values()
            for x in v
            if x["name"] == plugin_name
        )
    except StopIteration:
        raise ValueError(f"Plugin {plugin_name!r} not found in manifest") from None  # noqa: EM102, TRY003

    with _env_context(plugin["env"]):
        yield


@contextmanager
def schedule_context(schedule_name: str) -> Iterator[None]:
    """Establish a context within which a schedule can be run.

    All relevant env vars for the specified schedule will be set in the process
    for the duration of this context manager.

    Args:
        schedule_name: The name of the schedule to be run.

    Raises:
        ValueError: No schedule was found matching the given schedule name
            within the active manifest.

    Yields:
        `None`.
    """
    schedules = _get_active_manifest().data["schedules"]

    try:
        schedule = next(x for x in schedules if x["name"] == schedule_name)
    except StopIteration:
        raise ValueError(f"Schedule {schedule!r} not found in manifest") from None  # noqa: EM102, TRY003

    with _env_context(schedule["env"]):
        yield


@contextmanager
def job_context(job_name: str) -> Iterator[None]:
    """Establish a context within which a job can be run.

    All relevant env vars for the specified job will be set in the process for
    the duration of this context manager.

    Args:
        job_name: The name of the job to be run.

    Raises:
        ValueError: No job was found matching the given job name within the
            active manifest.

    Yields:
        `None`.
    """
    jobs = _get_active_manifest().data["jobs"]

    try:
        job = next(x for x in jobs if x["name"] == job_name)
    except StopIteration:
        raise ValueError(f"Job {job!r} not found in manifest") from None  # noqa: EM102, TRY003

    with _env_context(job["env"]):
        yield


# TODO: Provide a function which returns `_get_active_manifest().data` with
# env vars injected into each of its string fields, taking only from
# `os.environ`.
