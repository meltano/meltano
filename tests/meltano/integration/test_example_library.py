"""Pytest-based integration tests for the meltano example library.

Replaces the shell-driven ``integration/validate.sh`` + ``integration/commons.sh``
flow (see https://github.com/meltano/meltano/issues/6439).

Each integration test in ``integration/example-library/<name>/`` is a
doc-verification flow:

1. ``index.md`` is compiled to a shell script by ``integration/mdsh``.
2. The script is executed from the test's directory.
3. The resulting ``meltano.yml`` is diffed against ``ending-meltano.yml``.
4. If the test directory ships its own ``validate.sh``, it is run as an
   additional per-test behaviour assertion (mirrors the old shell flow).

The shared steps from ``commons.sh`` (logging.yaml injection, mdsh
compilation, the yaml diff assertion) are expressed as fixtures here, and
pytest removes the generated files automatically via ``tmp_path``.

Tests that require extra infrastructure (Postgres, S3) are skipped unless
the corresponding opt-in environment variable is set:

* ``MELTANO_TEST_POSTGRES=1`` — enable tests that need a Postgres warehouse
* ``MELTANO_TEST_S3=1`` — enable tests that need an S3-compatible endpoint
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

INTEGRATION_BASE_DIR = Path(__file__).resolve().parents[3] / "integration"
EXAMPLE_LIBRARY_DIR = INTEGRATION_BASE_DIR / "example-library"

# Tests that need extra infrastructure not available on a plain runner.
# Set the matching env var to opt in (see module docstring).
NEEDS_POSTGRES = {"meltano-run"}
NEEDS_S3 = {"meltano-state-s3"}

# Tests that require the full integration_tests.yml environment
# (uv sync --extra s3, dedicated runner, no pytest-xdist contention).
# These are exercised by the shell-driven integration/validate.sh flow in
# integration_tests.yml and are skipped under the regular test.yml matrix.
NEEDS_INTEGRATION_ENV = {
    "meltano-custom-python",
    "meltano-run-merge-states",
    "meltano-manifest",
    "meltano-expand-envvars-in-array",
}

# The source markdown document for every example-library test.
INDEX_MD = "index.md"
EXPECTED_MELTANO_YML = "ending-meltano.yml"
LOGGING_YAML = "logging.yaml"
PER_TEST_VALIDATE_SH = "validate.sh"


def _discover_example_library_tests() -> list[str]:
    """Return the names of every complete example-library integration test.

    A directory is only collected when it contains all three required
    fixtures (``index.md``, ``meltano.yml``, ``ending-meltano.yml``), so a
    half-finished example yields a clear collection-time skip instead of a
    cryptic runtime failure.
    """
    required = (INDEX_MD, "meltano.yml", EXPECTED_MELTANO_YML)
    return sorted(
        entry.name
        for entry in EXAMPLE_LIBRARY_DIR.iterdir()
        if entry.is_dir() and all((entry / name).is_file() for name in required)
    )


EXAMPLE_LIBRARY_TESTS = _discover_example_library_tests()


@pytest.fixture(scope="session")
def meltano_integration_base() -> Path:
    """The repository's ``integration`` directory."""
    return INTEGRATION_BASE_DIR


def _require_bash() -> str:
    """Return the bash executable, skipping the test when it is unavailable.

    Extracted from the ``bash_executable`` fixture so the "no bash" skip
    branch is directly exercisable by a unit test (bash always exists on the
    Linux CI matrix, so the branch would otherwise never be covered).
    """
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not available on this platform")
    return bash


@pytest.fixture
def bash_executable() -> str:
    """The bash interpreter used to run mdsh and the compiled scripts.

    Checked *before* mdsh because mdsh itself is a bash script — without
    bash there is no point probing for mdsh.
    """
    return _require_bash()


def _require_mdsh(meltano_integration_base: Path) -> Path:
    """Return the mdsh compiler, skipping the test when it is unavailable.

    Extracted from the ``mdsh_compiler`` fixture so both skip branches (no
    bash on PATH, no mdsh in the checkout) are directly exercisable by a
    unit test instead of being dead code on the Linux CI matrix.
    """
    _require_bash()
    mdsh = meltano_integration_base / "mdsh"
    if not mdsh.is_file():
        pytest.skip("mdsh is not available in this checkout")
    return mdsh


@pytest.fixture
def mdsh_compiler(meltano_integration_base: Path) -> Path:
    """The mdsh script used to compile ``index.md`` into a shell script.

    bash is probed first because mdsh itself is a bash script — without
    bash there is no point probing for mdsh.
    """
    return _require_mdsh(meltano_integration_base)


@pytest.fixture
def example_library_dir(meltano_integration_base: Path) -> Path:
    """The ``example-library`` directory containing the doc-based tests."""
    return meltano_integration_base / "example-library"


@pytest.fixture
def logging_yaml(meltano_integration_base: Path) -> Path:
    """The shared ``logging.yaml`` injected into each test directory."""
    return meltano_integration_base / "logging.yaml"


def _compile_script(bash: str, mdsh: Path, index_md: Path, output: Path) -> None:
    """Compile ``index.md`` into ``output`` using mdsh.

    Mirrors ``commons.sh``'s ``compile_script``. mdsh is invoked through
    bash explicitly so it works even when the file lacks the executable bit.
    """
    with output.open("w", encoding="utf-8") as fh:
        subprocess.run(
            [bash, str(mdsh), "-c", str(index_md)],
            check=True,
            stdout=fh,
            text=True,
        )
    output.chmod(0o755)


def _run_per_test_validate(bash: str, workdir: Path) -> None:
    """Run the test directory's own ``validate.sh`` if it ships one.

    The old shell flow allowed per-test validation scripts (e.g. asserting on
    run logs or persisted state); running them here preserves those behaviour
    assertions instead of silently dropping them.
    """
    validate_sh = workdir / PER_TEST_VALIDATE_SH
    if validate_sh.is_file():
        subprocess.run(
            [bash, "-xeuo", "pipefail", str(validate_sh)],
            cwd=workdir,
            check=True,
        )


@pytest.mark.parametrize("test_name", EXAMPLE_LIBRARY_TESTS)
def test_example_library(
    test_name: str,
    tmp_path: Path,
    bash_executable: str,
    mdsh_compiler: Path,
    example_library_dir: Path,
    logging_yaml: Path,
) -> None:
    """Run one example-library integration test end to end.

    Mirrors ``integration/validate.sh`` but runs inside ``tmp_path`` so
    pytest tears down all generated files automatically.
    """
    # The shell-driven integration/validate.sh flow only runs on Linux
    # (see integration_tests.yml: runs-on ubuntu-latest). mdsh compilation
    # and the compiled scripts are not portable to Windows/macOS bash, so
    # keep these doc-verification tests on the same platform boundary.
    if sys.platform != "linux":
        pytest.skip("example-library integration tests run on Linux only")

    # Skip tests that need infrastructure not opted into on this runner.
    if test_name in NEEDS_POSTGRES and not os.environ.get("MELTANO_TEST_POSTGRES"):
        pytest.skip("set MELTANO_TEST_POSTGRES=1 to run Postgres-backed tests")
    if test_name in NEEDS_S3 and not os.environ.get("MELTANO_TEST_S3"):
        pytest.skip("set MELTANO_TEST_S3=1 to run S3-backed tests")
    if test_name in NEEDS_INTEGRATION_ENV and not os.environ.get(
        "MELTANO_TEST_INTEGRATION_ENV"
    ):
        pytest.skip(
            "set MELTANO_TEST_INTEGRATION_ENV=1 to run tests that need the "
            "integration_tests.yml environment (full deps, dedicated runner)"
        )

    source_dir = example_library_dir / test_name

    # 1. Copy the test fixture files into the isolated working directory.
    #    This keeps the source checkout pristine (the old flow mutated
    #    the docs directory in place and required manual cleanup).
    for name in ("meltano.yml", "plugins", PER_TEST_VALIDATE_SH):
        src = source_dir / name
        if src.is_dir():
            shutil.copytree(src, tmp_path / name)
        elif src.is_file():
            shutil.copy2(src, tmp_path / name)

    # 2. Inject the shared logging config (commons.sh: inject_logging_yaml).
    shutil.copy2(logging_yaml, tmp_path / LOGGING_YAML)

    # 3. Compile index.md into a shell script (commons.sh: compile_script).
    script = tmp_path / f"{test_name}.sh"
    _compile_script(bash_executable, mdsh_compiler, source_dir / INDEX_MD, script)

    # 4. Run the compiled script from the test directory.
    env = os.environ.copy()
    env["MELTANO_PROJECT_ROOT"] = str(tmp_path)
    subprocess.run(
        [bash_executable, "-xeuo", "pipefail", str(script)],
        cwd=tmp_path,
        env=env,
        check=True,
    )

    # 5. Run per-test validation script if present (old flow: per-test
    #    validate.sh assertions on run logs / persisted state).
    _run_per_test_validate(bash_executable, tmp_path)

    # 6. Assert the resulting meltano.yml matches the expected one
    #    (commons.sh: check_meltano_yaml).
    result = tmp_path / "meltano.yml"
    expected = source_dir / EXPECTED_MELTANO_YML
    assert result.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8"), (
        f"meltano.yml for '{test_name}' does not match "
        f"'{EXPECTED_MELTANO_YML}'. Run with -vv to see the diff."
    )


@pytest.mark.parametrize(
    "missing_fixture",
    ["meltano_yml", "ending_meltano_yml"],
)
def test_discover_example_library_tests_skips_incomplete_directories(
    tmp_path, missing_fixture, monkeypatch
):
    """Regression: a directory that has ``index.md`` but is missing one of
    the other required fixtures must be skipped by the collector rather
    than silently included.

    Mirrors the original ``validate.sh`` behaviour, where the shell flow
    rejected a directory if any of the three files (``index.md``,
    ``meltano.yml``, ``ending-meltano.yml``) was missing. The pytest
    migration dropped that branch, which is what ``codecov/patch`` is
    flagging.
    """
    # Build two fixture directories: one complete, one missing a fixture.
    complete = tmp_path / "complete"
    complete.mkdir()
    for name in ("index.md", "meltano.yml", "ending-meltano.yml"):
        (complete / name).write_text(name)

    broken = tmp_path / "broken"
    broken.mkdir()
    for name in ("index.md", "meltano.yml", "ending-meltano.yml"):
        if (
            name
            != {
                "meltano_yml": "meltano.yml",
                "ending_meltano_yml": "ending-meltano.yml",
            }[missing_fixture]
        ):
            (broken / name).write_text(name)

    # Stray non-directory entry: ensures the ``entry.is_dir() == False``
    # branch of ``_discover_example_library_tests`` is also exercised
    # (codecov/patch was flagging it because every previous case created
    # only directories).
    (tmp_path / "stray.txt").write_text("not a test")

    # Point the module-level EXAMPLE_LIBRARY_DIR at our temp dir.
    # Use a module-object patch (importlib.resolve_name) rather than the
    # string-based ``monkeypatch.setattr``: under pytest-xdist each worker
    # imports the test module independently and the string-attribute form
    # silently rebinds a *copy* on some loaders, so the canonical module
    # used by ``_discover_example_library_tests`` is left untouched.
    import tests.meltano.integration.test_example_library as _tl_mod

    monkeypatch.setattr(_tl_mod, "EXAMPLE_LIBRARY_DIR", tmp_path)

    discovered = _tl_mod._discover_example_library_tests()
    assert "complete" in discovered
    assert "broken" not in discovered


def test_example_library_skip_guards_cover_env_dependent_branches(
    tmp_path, monkeypatch
):
    """Drive the skip guards of ``test_example_library`` that a Linux CI run
    cannot exercise on its own.

    * The ``sys.platform != "linux"`` guard never fires on the ubuntu matrix,
      so it has to be forced with a patched platform.
    * The infrastructure guards only fire when the corresponding test name is
      part of ``EXAMPLE_LIBRARY_TESTS`` *and* the opt-in env var is unset; the
      real example-library tree may not contain those names, so drive each one
      explicitly to keep ``codecov/patch`` at 100% regardless of the tree.
    """
    import tests.meltano.integration.test_example_library as _tl_mod

    def call_test(test_name: str):
        _tl_mod.test_example_library(
            test_name,
            tmp_path,
            "bash",
            tmp_path / "mdsh",
            tmp_path,
            tmp_path / "logging.yaml",
        )

    # Non-Linux guard: reachable only when the matrix runs on macOS/Windows.
    monkeypatch.setattr(_tl_mod.sys, "platform", "win32")
    with pytest.raises(pytest.skip.Exception):
        call_test("demo")

    # Infra guards: simulate a runner without the opt-in env vars.
    monkeypatch.setattr(_tl_mod.sys, "platform", "linux")
    for name, env_var in (
        ("meltano-run", "MELTANO_TEST_POSTGRES"),
        ("meltano-state-s3", "MELTANO_TEST_S3"),
        ("meltano-custom-python", "MELTANO_TEST_INTEGRATION_ENV"),
    ):
        monkeypatch.delenv(env_var, raising=False)
        with pytest.raises(pytest.skip.Exception):
            call_test(name)


def test_per_test_validate_and_bootstrap_guards(tmp_path, monkeypatch):
    """Cover helper and fixture branches that never fire against the real
    example-library tree or on Linux runners.

    * No example-library directory ships a ``validate.sh`` today, so the
      per-test assertion branch of ``_run_per_test_validate`` is dead in the
      integration run and needs a synthetic fixture.
    * ``bash`` and ``mdsh`` always exist on the ubuntu runners, so the
      "not available" skip branches of the ``bash_executable`` and
      ``mdsh_compiler`` fixtures are dead in CI and are forced here.
    """
    import tests.meltano.integration.test_example_library as _tl_mod

    # _run_per_test_validate: directory with a validate.sh -> assertion runs.
    validate_sh = tmp_path / "validate.sh"
    validate_sh.write_text(
        "#!/usr/bin/env bash\nset -e\necho per-test-validate-ok\n",
        encoding="utf-8",
    )
    _tl_mod._run_per_test_validate("bash", tmp_path)

    # _require_bash: no bash on PATH.
    monkeypatch.setattr(_tl_mod.shutil, "which", lambda _name: None)
    with pytest.raises(pytest.skip.Exception):
        _tl_mod._require_bash()

    # _require_mdsh: no bash on PATH.
    with pytest.raises(pytest.skip.Exception):
        _tl_mod._require_mdsh(tmp_path)

    # _require_mdsh: bash present but mdsh missing from the checkout.
    monkeypatch.setattr(_tl_mod.shutil, "which", lambda _name: "/usr/bin/bash")
    with pytest.raises(pytest.skip.Exception):
        _tl_mod._require_mdsh(tmp_path)
