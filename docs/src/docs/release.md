# Release

Meltano uses [semver](https://semver.org/) as its version number scheme.

## Requirements

::: warning Requirement
Ensure you have the latest `master` branch locally before continuing.
```bash
  # get latest master branch
  $ git fetch origin
```
:::

## Release process

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
