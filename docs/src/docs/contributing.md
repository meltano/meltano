# Contributing

## Prerequisites

In order to contribute to Meltano, you will need the following:

1. [Python 3.6.1+](https://www.python.org/downloads/)
2. [Node 8.11.0+](https://nodejs.org/)
3. [Yarn](https://yarnpkg.com/)

## Where to start?

We welcome contributions, idea submissions, and improvements. In fact we may already have open issues labeled [Accepting Merge Requests](https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&label_name[]=Accepting%20Merge%20Requests) if you don't know where to start. Please see the contribution guidelines below for source code related contributions.

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
python -m venv ~/virtualenvs/meltano-development

# Activate your virtual environment
source ~/virtualenvs/meltano-development/bin/activate

# Install all the dependencies
pip install -r requirements.txt

# Install dev dependencies with the edit flag on to detect changes
# Note: you may have to escape the .`[dev]` argument on some shells, like zsh
pip install -e .[dev]

# Bundle the Meltano UI into the `meltano` package
make bundle
```

Meltano is now installed and available at `meltano`, as long as you remain in your `meltano-development` virtual environment!

This means that you're ready to start Meltano CLI development. For API and UI development, read on.

### Metrics (anonymous usage data) tracking

As you contribute to Meltano, you may want to disable [metrics tracking](/docs/environment-variables.html#anonymous-usage-data) globally rather than by project. You can do this by setting the environment variable `MELTANO_DISABLE_TRACKING` to `True`:

```bash
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
export MELTANO_DISABLE_TRACKING=True
```

## Meltano API Development

For all changes that do not involve working on Meltano UI (front-end) itself, run the following command:

```bash
# Starts both a development build of the Meltano API and a production build of Meltano UI
FLASK_ENV=development meltano ui
```

The development build of the Meltano API should be available at <http://localhost:5000/>.

:::warning Troubleshooting
If you run into `/bin/sh: yarn: command not found`, double check that you've got [the prerequisites](https://www.meltano.com/docs/contributing.html#prerequisites) installed.

On macOS, this can be solved by running `brew install yarn`.
:::

## Meltano UI Development

In the event you are contributing to Meltano UI and want to work with all of the frontend tooling (i.e., hot module reloading, etc.), you will need to run the following commands:

```bash
# Navigate to a Meltano project that has already been initialized
# Start the Meltano API and a production build of Meltano UI that you can ignore
meltano ui

# Open a new terminal tab and go to your meltano directory
# Install frontend infrastructure at the root directory
yarn setup

# Start local development environment
yarn serve
```

The development build of the Meltano UI will be available at <http://localhost:8080/>.

If you need to change the URL of your development environment, you can do this by updating your `.env` in your project directory with the following configuration:

```bash
# The URL where the web app will be located when working locally in development
# since it provides the redirect after authentication.
# Not require for production
export MELTANO_UI_URL = ""
```

## Meltano System Database

Meltano API and CLI are both supported by a database that is managed using Alembic migrations.

:::tip Note
[Alembic](https://alembic.sqlalchemy.org/en/latest/) is a full featured database migration working on top of SQLAlchemy.
:::

Migrations for the system database are located inside the `meltano.migrations` module.

To create a new migration, use the `alembic revision -m "message"` command, then edit the created file with the necessary database changes. Make sure to implement both `upgrade` and `downgrade`, so the migration is reversible, as this will be used in migration tests in the future.

Each migration should be isolated from the `meltano` module, so **don't import any model definition inside a migration**.

:::warning
Meltano doesn't currently support auto-generating migration from the models definition.
:::

To run the migrations, use `meltano upgrade` inside a Meltano project.

## Documentation

### Text

Follow the [Merge Requests](#merge-requests) and [Changelog](#changelog) portions of this contribution section for text-based documentation contributions.

### Images

When adding supporting visuals to documentation, adhere to:

- Use Chrome in "incognito mode" (we do this to have the same browser bar for consistency across screenshots)
- Screenshot the image at 16:9 aspect ratio with minimum 1280x720px
- Place `.png` screenshot in `src/docs/.vuepress/public/screenshots/` with a descriptive name

## Testing

### End-to-End Testing with Cypress

Our end-to-end tests are currently being built with [Cypress](https://www.cypress.io/).

#### How to Run Tests

1. Initialize a new meltano project with `meltano init $PROJECT_NAME`
1. Change directory into `$PROJECT_NAME`
1. Start up project with `meltano ui`
1. Clone Meltano repo
1. Open Meltano repo in Terminal
1. Run `yarn setup`
1. Run `yarn test:e2e`

This will kick off a Cypress application that will allow you to run tests as desired by clicking each test suite (which can be found in `/src/tests/e2e/specs/*.spec.js`)

![Preview of Cypres app running](/images/cypress-tests/cypTest-01.png)

::: info
In the near future, all tests can flow automatically; but there are some complications that require manual triggering due to an inability to read pipeline completion.
:::

## Code style

### Tools

Meltano uses the below tools to enforce consistent code style. Explore the [repo](https://gitlab.com/meltano/meltano/tree/master) to learn of the specific rules and settings of each.

- [Black](https://github.com/ambv/black)
- [ESLint](https://eslint.org/docs/rules/)
- [ESLint Vue Plugin](https://github.com/vuejs/eslint-plugin-vue)
- [Prettier](https://prettier.io/)

You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

### Mantra

> A contributor should know the exact line-of-code to make a change based on convention

In the spirit of GitLab's "boring solutions" with the above tools and mantra, the frontend codebase is additionally sorted as follows:

- `import`s are alphabetical and subgrouped by _core_ -> _third-party_ -> _application_ with a return delineating. For example:

  ```js
  // core
  import Vue from 'vue'
  // third-party
  import lodash from 'lodash'
  // application
  import poller from '@/utils/poller'
  import utils from '@/utils/utils'
  ```

- object properties and methods are alphabetical where `Vuex` stores are the exception (`defaultState` -> `getters` -> `actions` -> `mutations`)

Over time we hope to automate the enforcement of the above sorting rules.

:::warning Troubleshooting
When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.
:::

## UI/UX

### Visual Hierarchy

#### Depth

The below level hierarchy defines the back to front depth sorting of UI elements. Use it as a mental model to inform your UI decisions.

- Level 1 - Primary navigation, sub-navigation, and signage - _Grey_
- Level 2 - Task container (traditionally the page metaphor) - _White-ish Grey_
- Level 3 - Primary task container(s) - _White w/Shadow_
- Level 4 - Dropdowns, dialogs, pop-overs, etc. - _White w/Shadow_
- Level 5 - Modals - _White w/Lightbox_
- Level 6 - Toasts - _White w/Shadow + Message Color_

#### Interactivity

Within each aforementioned depth level is an interactive color hierarchy that further organizes content while communicating an order of importance for interactive elements. This interactive color hierarchy subtly influences the user's attention and nudges their focus.

1. Primary - _`$interactive-primary`_
   - Core interactive elements (typically buttons) for achieving the primary task(s) in the UI
   - Fill - Most important
   - Stroke - Important
1. Secondary - _`$interactive-secondary`_
   - Supporting interactive elements (various controls) that assist the primary task(s) in the UI
   - Fill - Most important
     - Can be used for selected state (typically delegated to stroke) for grouped buttons (examples usage seen in Entity Selection and Transform defaults)
   - Stroke - Important
     - Denotes the states of selected, active, and/or valid where grey represents the opposites unselected, inactive, and/or invalid
1. Tertiary - _Greyscale_
   - Typically white buttons and other useful controls that aren't core or are in support of the primary task(s) in the UI
1. Navigation - _`$interactive-navigation`_
   - Denotes navigation and sub-navigation interactive elements as distinct from primary and secondary task colors

After the primary, secondary, tertiary, or navigation decision is made, the button size decision is informed by:

1. Use the default button size
1. Use the `is-small` modifier if it is within a component that can have multiple instances

### Markup Hierarchy

There are three fundamental markup groups in the codebase. All three are technically VueJS single-file components but each have an intended use:

1. Views (top-level "pages" and "page containers" that map to parent routes)
2. Sub-views (nested "pages" of "page containers" that map to child routes)
3. Components (widgets that are potentially reusable across parent and child routes)

Here is a technical breakdown:

1. Views - navigation, signage, and sub-navigation
   - Navigation and breadcrumbs are adjacent to the main view
   - Use `<router-view-layout>` as root with only one child for the main view:
     1. `<div class="container view-body">`
        - Can expand based on task real-estate requirements via `is-fluid` class addition
   - Reside in the `src/views` directory
2. Sub-views - tasks
   - Use `<section>` as root (naturally assumes a parent of `<div class="container view-body">`) with one type of child:
     - One or more `<div class="columns">` each with their needed `<div class="column">` variations
   - Reside in feature directory (ex. `src/components/analyze/AnalyzeModels`)
3. Components - task helpers
   - Use Vue component best practices
   - Reside in feature or generic directory (ex. `src/components/analyze/ResultTable` and `src/components/generic/Dropdown`)

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

## Demo Day

For each demo day, we need to ensure that the following process is followed:

### Demo Day: Setup

1. Document list of features to demo
2. Document order of people demoing
3. Ensure every person demoing has proper display size (i.e., font sizes, zoomed in enough, etc.)
   - Font size at least 20px
   - Browser zoom at least 125%

### Demo Day: Workflow

1. Record each meeting with Zoom
2. Generate list of timestamps for each featured demo
3. Generate list of features (from Setup section) paired with timestamps
4. Upload recording to YouTube
5. Add features + timestamps to YouTube description

## Releases

### Versioning

Meltano uses [semver](https://semver.org/) as its version number scheme.

### Prerequisites

Ensure you have the latest `master` branch locally before continuing.

```bash
git fetch origin
```

### Release Process

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.

1. Meltano has a number of dependencies for the release toolchain that are required when performing a release. If you haven't already, please navigate to your meltano install and run the following command to install all development dependencies:

   ```bash
   # activate your virtualenv
   source ./venv/bin/activate

   # pip install all the development dependencies
   pip install .[dev]
   ```

1. Execute the commands below:

   ```bash
   # create and checkout the `release-next` branch from `origin/master`
   git checkout -B release-next origin/master

   # view changelog (verify changes made match changes logged)
   changelog view

   # after the changelog has been validated, tag the release
   make release

   # ensure the tag once the tag has been created, check the version we just bumped to: e.g. `0.22.0` => `0.23.0`.
   git describe --tags --abbrev=0

   # push the tag upstream to trigger the release pipeline
   git push origin $(git describe --tags --abbrev=0)

   # push the release branch to merge the new version, then create a merge request
   git push origin release-next
   ```

:::tip Releasing a hotfix?
You can use `make type=patch release` to force a patch release. This is useful when we need to release hotfixes.
:::

1. Create a merge request from `release-next` targeting `master` and make sure to check `delete the source branch when the changes are merged`.
1. Add the pipeline link (the one that does the actual deployment) to the merge request. Go to the commit's pipelines tab and select the one that has the **publish** stage.
1. When the **publish** pipeline succeeds, the release is publicly available on [PyPI](https://pypi.org/project/meltano/).
1. Follow the [Digital Ocean publish process](#digitalocean-marketplace)
1. If a non-patch release, record and distribute the [Speedrun Video](#speedruns)

## DigitalOcean Marketplace

Meltano is deployed and available as a <a :href="$site.themeConfig.data.digitalOceanUrl">DigitalOcean Marketplace 1-Click install</a>.

### Build the snapshot

The `distribute` step in the CI/CD pipeline has a manual action named _digitalocean_marketplace_ that will use Packer to create a snapshot with the latest version of Meltano installed and ready.

:::tip Master only
The _digitalocean_marketplace_ job is only available on pipelines running off `master`.
:::

1. Click the "Play" button associated with this _digitalocean_marketplace_ `distribute` step
1. The snapshot string should be available under `meltano-<timestamp>` on DigitalOcean, which you will find at the bottom of the _digitalocean_marketplace_ job. Take note of this snapshot string as you'll use it in the next step.

### Update the DigitalOcean listing

Then, head to the DigitalOcean vendor portal at <https://marketplace.digitalocean.com/vendorportal> to edit the Meltano listing.

:::tip Don't see the Meltano listing?
You'll have to be granted access to the DigitalOcean vendor portal. Please ask access to your manager.
:::

1. Once inside the listing, update the following entries:
    - **System Image** to the new image (match the aforementioned snapshot string)
    - **Version** to the latest Meltano version
    - **Meltano Package Version** inside the _Software Included Entry_
1. Submit it for review to finish the process.

## Speedruns

::: info
🏆 Current Record: 1:35 (Ben Hong)
:::

::: tip
Remember to leave each screen up for at least 2 seconds so users have a chance to notice that something actually happened.
:::

### Requirements

1. Use `tap-gitlab` and `target-postgres` (real example, not Carbon Intensity)
1. Keep keystrokes to a minimum (ideally zero)
1. You do not have to explain every step
1. Do not need to stop and explain new features
1. Time starts from when the webapp is loaded on the browser
1. Must complete the following tasks
   - Install an extractor
   - Select entities
   - Install and configure loader
   - Configure transform
   - Configure and run pipeline
   - Open Model
   - Generate SQL query with data model
   - Render chart based on query
   - Save query as a report with auto-populated name
   - Create new dashboard with auto-populated name
   - Add saved report to new dashboard
   - Verify dashboard contains report

### Workflow

1. Introduce Meltano to new users:

```
Meltano is an open source data toolkit
that makes it easy to go from data source to dashboard.

For more information, check us out at meltano.com!
```

2. Check that Meltano does not exist on your machine

```bash
meltano --version
# command not found: meltano
```

3. Install Meltano on your machine using distributed version

```bash
pip install meltano
```

4. Check Meltano version matches latest release

```bash
meltano --version
```

5. Create a new Meltano project

```bash
meltano init speedrun-workflow
```

6. Change directory into your new project

```bash
cd speedrun-workflow
```

7. Start Meltano application

```
meltano ui
```

8. Assuming there are no conflicts on the port, you can now open your Meltano instance at http://localhost:5000.

9. Run through [Getting Started Guide](/docs/getting-started.html) as quickly as possible with some narration, but don't pause mid-action to explain something.

## Taps & Targets Workflow

### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target development please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitLab
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

### Discoverability

We maintain a curated list of taps/targets that are expected to work out of the box with Meltano. Meltano also helps the CLI user find components via a `discover` command.

Get a list of extractors:

```bash
meltano discover extract
tap-demo==...
tap-zendesk==1.3.0
tap-marketo==...
...
```

Or a list of loaders

```bash
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
cd path/to/meltano
MELTANO_VENV=.venv tmuxinator local
```

### Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)
