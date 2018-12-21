# Contributing

We welcome contributions and improvements, please see the contribution guidelines below:

## Getting Setup

```bash
# Clone the Meltano repo
git clone git@gitlab.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Activate your virtual environment
source ./venv/bin/activate

# Install dependencies with the edit flag on to detect changes
pip install -e .

# Run Meltano APIs
python -m meltano.api
```

Open a new terminal tab in the meltano project directory:

```bash
# Change into the Meltano Analyze code directory
cd src/analyze

# Install the dependencies for Meltano Analyze
npm install

# Start the web server for Meltano Analyze 
npm run dev
```

## Code style

Meltano uses [Black](https://github.com/ambv/black) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

You can also have black run automatically using a `git` hook. See https://github.com/ambv/black#version-control-integration for more details.

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