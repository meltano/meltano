"""Pytest-based integration tests for the meltano example library.

Replaces the shell-driven ``integration/validate.sh`` + ``integration/commons.sh``
flow (see https://github.com/meltano/meltano/issues/6439).

Each integration test in ``integration/example-library/<name>/`` is a
doc-verification flow:

1. ``index.md`` is compiled to a shell script by ``integration/mdsh``.
2. The script is executed from the test's directory.
3. The resulting ``meltano.yml`` is diffed against ``ending-meltano.yml``.

The shared steps from ``commons.sh`` (logging.yaml injection, mdsh
compilation, the yaml diff assertion) are expressed as fixtures here, and
pytest removes the generated files automatically via ``tmp_path``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

INTEGRATION_BASE_DIR = Path(__file__).resolve().parents[3] / "integration"
EXAMPLE_LIBRARY_DIR = INTEGRATION_BASE_DIR / "example-library"

# Tests that need extra infrastructure not available on a plain runner.
NEEDS_POSTGRES = {"meltano-run"}
NEEDS_S3 = {"meltano-state-s3"}

# The source markdown document for every example-library test.
INDEX_MD = "index.md"
EXPECTED_MELTANO_YML = "ending-meltano.yml"
LOGGING_YAML = "logging.yaml"


def _discover_example_library_tests() -> list[str]:
    """Return the names of every example-library integration test."""
    return sorted(
        entry.name
        for entry in EXAMPLE_LIBRARY_DIR.iterdir()
        if entry.is_dir() and (entry / INDEX_MD).is_file()
    )


EXAMPLE_LIBRARY_TESTS = _discover_example_library_tests()


@pytest.fixture(scope="session")
def meltano_integration_base() -> Path:
    """The repository's ``integration`` directory."""
    return INTEGRATION_BASE_DIR


@pytest.fixture
def mdsh_compiler(meltano_integration_base: Path) -> Path:
    """The mdsh script used to compile ``index.md`` into a shell script."""
    mdsh = meltano_integration_base / "mdsh"
    if not mdsh.is_file():
        pytest.skip("mdsh is not available in this checkout")
    return mdsh


@pytest.fixture
def example_library_dir(meltano_integration_base: Path) -> Path:
    """The ``example-library`` directory containing the doc-based tests."""
    return meltano_integration_base / "example-library"


@pytest.fixture
def logging_yaml(meltano_integration_base: Path) -> Path:
    """The shared ``logging.yaml`` injected into each test directory."""
    return meltano_integration_base / "logging.yaml"


def _compile_script(mdsh: Path, index_md: Path, output: Path) -> None:
    """Compile ``index.md`` into ``output`` using mdsh.

    Mirrors ``commons.sh``'s ``compile_script``.
    """
    with output.open("w", encoding="utf-8") as fh:
        subprocess.run(
            [str(mdsh), "-c", str(index_md)],
            check=True,
            stdout=fh,
            text=True,
        )
    output.chmod(0o755)


@pytest.mark.parametrize("test_name", EXAMPLE_LIBRARY_TESTS)
def test_example_library(
    test_name: str,
    tmp_path: Path,
    mdsh_compiler: Path,
    example_library_dir: Path,
    logging_yaml: Path,
) -> None:
    """Run one example-library integration test end to end.

    Mirrors ``integration/validate.sh`` but runs inside ``tmp_path`` so
    pytest tears down all generated files automatically.
    """
    source_dir = example_library_dir / test_name

    # 1. Copy the test fixture files into the isolated working directory.
    #    This keeps the source checkout pristine (the old flow mutated
    #    the docs directory in place and required manual cleanup).
    for name in ("meltano.yml", "plugins"):
        src = source_dir / name
        if src.is_dir():
            shutil.copytree(src, tmp_path / name)
        elif src.is_file():
            shutil.copy2(src, tmp_path / name)

    # 2. Inject the shared logging config (commons.sh: inject_logging_yaml).
    shutil.copy2(logging_yaml, tmp_path / LOGGING_YAML)

    # 3. Compile index.md into a shell script (commons.sh: compile_script).
    script = tmp_path / f"{test_name}.sh"
    _compile_script(mdsh_compiler, source_dir / INDEX_MD, script)

    # 4. Run the compiled script from the test directory.
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not available on this platform")
    env = os.environ.copy()
    env["MELTANO_PROJECT_ROOT"] = str(tmp_path)
    subprocess.run(
        [bash, "-xeuo", "pipefail", str(script)],
        cwd=tmp_path,
        env=env,
        check=True,
    )

    # 5. Assert the resulting meltano.yml matches the expected one
    #    (commons.sh: check_meltano_yaml).
    result = tmp_path / "meltano.yml"
    expected = source_dir / EXPECTED_MELTANO_YML
    assert result.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8"), (
        f"meltano.yml for '{test_name}' does not match "
        f"'{EXPECTED_MELTANO_YML}'. Run with -vv to see the diff."
    )
