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
from contextvars import ContextVar

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from meltano.core.manifest.manifest import Manifest

from meltano.core.utils import EnvVarMissingBehavior, expand_env_vars


def _expand_env_vars_multi_pass(
    env_dict: Mapping[str, str], base_env: Mapping[str, str]
) -> dict[str, str]:
    """Expand environment variables with multiple passes to handle dependencies.

    Args:
        env_dict: Dictionary of environment variables to expand
        base_env: Base environment to use for expansion

    Returns:
        Fully expanded environment dictionary
    """
    if not env_dict:
        return {}

    # Start with the base environment
    combined_env = dict(base_env)
    result = dict(env_dict)

    # Keep expanding until no changes occur
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        # Update combined environment with current results
        combined_env.update(result)

        # Expand all variables using the combined environment
        new_result = expand_env_vars(
            env_dict,
            combined_env,
            if_missing=EnvVarMissingBehavior.ignore,
        )

        # Check if we've reached a fixed point
        if new_result == result:
            break

        result = new_result

    return result


_active_manifest: ContextVar[Manifest | None] = ContextVar(
    "active_manifest",
    default=None,
)
_active_plugin: ContextVar[str | None] = ContextVar("active_plugin", default=None)
_active_schedule: ContextVar[str | None] = ContextVar("active_schedule", default=None)
_active_job: ContextVar[str | None] = ContextVar("active_job", default=None)


def _get_active_manifest() -> Manifest:
    manifest = _active_manifest.get()
    if manifest is None:
        raise Exception("No manifest has been activated") from None  # noqa: EM101
    return manifest


@contextmanager
def _manifest_context(manifest: Manifest) -> Iterator[None]:
    token = _active_manifest.set(manifest)
    try:
        yield
    finally:
        _active_manifest.reset(token)


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
    # Use multi-pass expansion to handle dependencies between env vars
    manifest_env = manifest.data.get("env", {})
    if not manifest_env:
        manifest_env = {}
    expanded_env = _expand_env_vars_multi_pass(manifest_env, os.environ)

    with _manifest_context(manifest), _env_context(expanded_env):
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
    try:
        manifest = _get_active_manifest()
    except Exception:
        # No active manifest, context does nothing
        yield
        return

    try:
        plugin = next(
            x
            for v in manifest.data["plugins"].values()
            for x in v
            if x["name"] == plugin_name
        )
    except StopIteration:
        # Plugin not found, context does nothing
        yield
        return

    # Track the active plugin
    plugin_token = _active_plugin.set(plugin_name)

    # Use multi-pass expansion to handle dependencies, using current os.environ
    # which includes manifest vars already set
    plugin_env = plugin.get("env", {})
    expanded_env = _expand_env_vars_multi_pass(plugin_env, os.environ)

    try:
        with _env_context(expanded_env):
            yield
    finally:
        _active_plugin.reset(plugin_token)


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
    try:
        schedules = _get_active_manifest().data.get("schedules", [])
    except Exception:
        # No active manifest, context does nothing
        yield
        return

    try:
        schedule = next(x for x in schedules if x["name"] == schedule_name)
    except StopIteration:
        raise ValueError(f"Schedule {schedule_name!r} not found in manifest") from None  # noqa: EM102

    # Track the active schedule
    schedule_token = _active_schedule.set(schedule_name)

    # Use multi-pass expansion to handle dependencies
    schedule_env = schedule.get("env", {})
    expanded_env = _expand_env_vars_multi_pass(schedule_env, os.environ)

    try:
        with _env_context(expanded_env):
            yield
    finally:
        _active_schedule.reset(schedule_token)


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
    try:
        jobs = _get_active_manifest().data.get("jobs", [])
    except Exception:
        # No active manifest, context does nothing
        yield
        return

    try:
        job = next(x for x in jobs if x["name"] == job_name)
    except StopIteration:
        raise ValueError(f"Job {job_name!r} not found in manifest") from None  # noqa: EM102

    # Track the active job
    job_token = _active_job.set(job_name)

    # Use multi-pass expansion to handle dependencies
    job_env = job.get("env", {})
    expanded_env = _expand_env_vars_multi_pass(job_env, os.environ)

    try:
        with _env_context(expanded_env):
            yield
    finally:
        _active_job.reset(job_token)


def get_expanded_manifest_data() -> dict[str, t.Any]:
    """Get the active manifest data with env vars expanded from os.environ.

    Returns:
        The manifest data with all string values having environment variables
        expanded using the current os.environ.

    Raises:
        Exception: If no manifest has been activated.
    """
    manifest = _get_active_manifest()
    return expand_env_vars(manifest.data, os.environ)


def get_active_manifest_with_env() -> dict[str, t.Any] | None:
    """Get the active manifest with expanded environment variables.

    Returns:
        The manifest data with expanded env vars, or None if no active manifest.
    """
    manifest = _active_manifest.get()
    if manifest is None:
        return None

    # Return a copy of the manifest data with expanded env vars
    manifest_data = manifest.data.copy()
    if "env" in manifest_data:
        manifest_data["env"] = expand_env_vars(manifest_data["env"], os.environ)

    return manifest_data
