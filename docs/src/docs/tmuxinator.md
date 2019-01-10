# Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

## Why Tmuxinator?

In order to run applications, you need to run multiple sessions and have to do a lot of repetitive tasks (like sourcing your virtual environments). So we have created a way for you to start and track everything in its appropriate panes with a single command. 

1. Start up Docker
1. Start Meltano API
1. Start the web app

It's a game changer for development and it's worth the effort!

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
