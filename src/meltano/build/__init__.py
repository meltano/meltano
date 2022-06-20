"""A PEP 517 build backend for Meltano that automatically installs shell tab-completions."""

import os
from pathlib import Path
from platform import system
from shutil import copy

from poetry.core.masonry import api  # noqa: F401


BUILD_DIR = Path(__file__).parent
HOME = Path.home()
PERMISSION = 0o755


def install_completions(src: Path, dest: Path, name: str) -> Path:
    """Copy `src` into `dest` with the given name & create directories as needed.

    Parameters:
        src: The path to the Meltano tab-completion script for the target shell.
        dest: The directory into which the script should be copied.
        name: The name the script should have within `dest`.

    Returns:
        The location the Meltano completions script was installed in.
    """
    dest.mkdir(parents=True, exist_ok=True)
    installation_location = Path(copy(src, dest / name))
    installation_location.chmod(PERMISSION)
    return installation_location


def install_bash_completions() -> Path:
    """Install Meltano tab-completion for Bash.

    Returns:
        The location the Meltano completions script was installed in.
    """
    # Installs into:
    # ${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions
    return install_completions(
        BUILD_DIR / "meltano-complete.bash",
        (
            Path(
                os.environ.get(
                    "BASH_COMPLETION_USER_DIR",
                    Path(os.environ.get("XDG_DATA_HOME", HOME / ".local" / "share"))
                    / "bash-completion",
                )
            )
            / "completions"
        ),
        "meltano",
    )


def install_fish_completions() -> Path:
    """Install Meltano tab-completion for Fish.

    Returns:
        The location the Meltano completions script was installed in.
    """
    dest = HOME / ".config" / "fish" / "completions"
    return install_completions(
        BUILD_DIR / "meltano-complete.fish", dest, "meltano.fish"
    )


def install_zsh_completions() -> Path:
    """Install Meltano tab-completion for Zsh.

    Directories in `$FPATH` are attempted until one works, or there are none left. By default all
    directories on `$FPATH` are owned by root, but it's common for users to add one or more user
    directories to it.

    Raises:
        Exception: No location in `$FPATH` was suitable for installation.

    Returns:
        The location the Meltano completions script was installed in.
    """
    for dest in os.environ.get("FPATH", "").split(":"):
        if dest == "":
            continue
        try:
            return install_completions(
                BUILD_DIR / "meltano-complete.zsh", Path(dest), "_meltano"
            )
        except OSError:
            pass
    raise Exception


if system() != "Windows":
    for shell, fn in {
        "bash": install_bash_completions,
        "fish": install_fish_completions,
        "zsh": install_zsh_completions,
    }.items():
        try:
            installation_location = fn()
        except Exception:
            print(  # noqa: WPS421
                f"Failed to install {shell} tab-completions for Meltano"
            )
        else:
            print(  # noqa: WPS421
                f"Installed {shell} tab-completions for Meltano at {installation_location}"
            )
