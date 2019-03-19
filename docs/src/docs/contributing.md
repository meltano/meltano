# Contributing

We welcome contributions and improvements, please see the contribution guidelines below:

## Installation from source

```bash
# Clone the Meltano repo
git clone git@gitlab.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Optional, but it's best to have the latest pip
pip install --upgrade pip

# Optional, but it's best to have the latest setuptools
pip install --upgrade setuptools

# Optional, but it's recommended to create a virtual environment
# in order to minimize side effects from unknown environment variable
python -m venv venv

# Activate your virtual environment
source ./venv/bin/activate

# Install all the dependencies
pip install -r requirements.txt

# Install dev dependencies with the edit flag on to detect changes
pip install -e '.[dev]'

# Run scripts to create remaining required files
make bundle
```

Meltano is now installed and available at `meltano`.

Head out to the [tutorials](/docs/tutorial.html) to create your first project.


### Meltano API Development

For all changes that do not involve working on Meltano UI itself, run the following command:

```bash
# Starts both Meltano API and a production build of Meltano UI
meltano ui
```

### Meltano UI Development

In the event you are contributing to Meltano UI and want to work with all of the frontend tooling (i.e., hot module reloading, etc.), you will need to run the following commands:

```bash
# Starts the Meltano API and a production build of Meltano UI that you can ignore
meltano ui

# Open a new terminal tab and go to your meltano directory. Then change directory to analyze
cd src/analyze

# Install dependencies
npm install # or yarn

# Start local development environment
npm run dev # or yarn dev
```

## Code style

Meltano uses [Black](https://github.com/ambv/black) and [ESLint](https://eslint.org/docs/rules/) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

## Merge Requests

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer should approve the merge request
1. Once approved, the merge request can be merged by any Meltano maintainer

## Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

## Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.

## Releases

Meltano uses [semver](https://semver.org/) as its version number scheme.

### Prerequisites
Ensure you have the latest `master` branch locally before continuing.
```bash
  # get latest master branch
  $ git fetch origin
```

### Release process

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.
1. Meltano has a number of dependencies for the deployment toolchain that are required when performing a release. If you haven't already, please navigate to your meltano install and run the following command to install dev dependencies:
    ```bash
    # activate your virtualenv
    $ source ./venv/bin/activate

    # pip install all the development dependencies
    $ pip install '.[dev]'
    ```
1. Execute the commands below:
    ```bash
    # if you've released before, you may need to delete the last local release branch you created
    $ git branch -D release-next

    # create and checkout release-next branch that's based off master branch
    $ git checkout -b release-next origin/master

    # view changelog (verify changes made match changes logged)
    $ changelog view

    # after changelog validation, build the release
    $ make release

    # validate that the tag auto increments based on semver
    $ git push --tags

    # update meltano repo with release-next branch
    $ git push origin release-next
    ```
1. Create a merge request from `release-next` targeting `master` and make sure to check `delete the source branch when the changes are merged`.
1. Add the pipeline link (the one that does the actual deployment) to the merge request. Go to the commit's pipelines tab and select the one that has the **publish** stage.
1. When the **publish** pipeline succeeds, the release is publicly available.

## Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

### Why Tmuxinator?

In order to run applications, you need to run multiple sessions and have to do a lot of repetitive tasks (like sourcing your virtual environments). So we have created a way for you to start and track everything in its appropriate panes with a single command.

1. Start up Docker
1. Start Meltano API
1. Start the web app

It's a game changer for development and it's worth the effort!

### Requirements

1. [tmux](https://github.com/tmux/tmux) - Recommended to install with brew
1. [tmuxinator](https://github.com/tmuxinator/tmuxinator)

This config uses `$MELTANO_VENV` to source the virtual environment from. Set it to the correct directory before running tmuxinator. 

### Instructions

1. Make sure you know what directory your virtual environment is. It is normally `.venv` by default.
1. Run the following commands. Keep in mind that the `.venv` in line 2 refers to your virtual environment directory in Step #1.

```bash
$ cd path/to/meltano
$ MELTANO_VENV=.venv tmuxinator local
```

### Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)
