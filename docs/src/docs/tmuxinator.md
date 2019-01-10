# Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

## Requirements

1. [tmux](https://github.com/tmux/tmux) - Recommended to install with brew
1. [tmuxinator](https://github.com/tmuxinator/tmuxinator)

This config uses `$MELTANO_VENV` to source the virtual environment from. Set it to the correct directory before running tmuxinator. 

## Instructions

1. Make sure you know what directory your virtual environment is. It is normally `.venv` by default.
1. Run the following commands. Keep in mind that the `.venv` in line 2 refers to your virtual environment directory in Step #1. 

```bash
$ cd path/to/meltano
$ MELTANO_VENV=.venv tmuxinator local
```

## Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)
