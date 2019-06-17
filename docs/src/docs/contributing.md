# Contributing

**Note: Meltano uses >= python3.6**

We welcome contributions, idea submissions, and improvements. In fact we may already have open issues labeled [Accepting Merge Requests](https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=Accepting%20Merge%20Requests) if you don't know where to start. Please see the contribution guidelines below for source code related contributions:

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
# Note: you may have to escape the `.[dev]` argument on some shells, like zsh
pip install -e .[dev]

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

## Documentation

### Text

Follow the merge request and changelog portions of this contribution section for text-based documentation contributions.

### Images

When adding supporting visuals to documentation, adhere to:
- Use Chrome in "incognito mode" (we do this to have the same browser bar for consistency across screenshots)
- Screenshot the image at 16:9 aspect ratio with minimum 1280x720px
- Place `.png` screenshot in `src/docs/.vuepress/public/screenshots/` with a descriptive name

## Code style

Meltano uses [Black](https://github.com/ambv/black) and [ESLint](https://eslint.org/docs/rules/) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

:::warning Troubleshooting
When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.
:::

## Merge Requests

:::tip Searching for something to work on?
Start off by looking at our [~"Accepting Merge Request"](https://gitlab.com/meltano/meltano/issues?label_name=Accepting+Merge+Requests) label.

Keep in mind that this is only a suggestion: all improvements are welcome.
:::

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer may approve the merge request or send it back for further iteration
1. Once approved, the merge request can be merged by any Meltano maintainer

### Reviews

A contributor can ask for a review on any merge request, without this merge request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the merge request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a merge request without feedback, unless specified by the reviewer.

## Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

### Script

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
    $ pip install .[dev]
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

    # after building the release, check the version we just bumped to: e.g. `0.22.0` => `0.23.0`.
    # occasionally the version bump can go to a version you don't expect.
    $ changelog view

    # validate that the tag auto increments based on semver
    $ git push --tags

    # update meltano repo with release-next branch
    $ git push origin release-next
    ```
1. Create a merge request from `release-next` targeting `master` and make sure to check `delete the source branch when the changes are merged`.
1. Add the pipeline link (the one that does the actual deployment) to the merge request. Go to the commit's pipelines tab and select the one that has the **publish** stage.
1. When the **publish** pipeline succeeds, the release is publicly available.

## Taps & Targets Workflow

### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target developement please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitLab
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

### Discoverability

We will maintain a curated list of taps/targets that are expected to work out of the box with Meltano.

Meltano should help the end-user find components via a `discover` command:

```
$ meltano discover extract
tap-demo==...
tap-zendesk==1.3.0
tap-marketo==...
...

$ meltano discover load
target-demo==...
target-snowflake==git+https://gitlab.com/meltano/target-snowflake@master.git
target-postgres==...
```

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
