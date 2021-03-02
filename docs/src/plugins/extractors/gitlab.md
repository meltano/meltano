---
sidebar: auto
description: Use Meltano to pull data from the GitLab API and load it into Snowflake, PostgreSQL, and more
---

# GitLab

The `tap-gitlab` [extractor](/plugins/extractors/) pulls data from the [GitLab API](https://docs.gitlab.com/ee/api/).

- **Repository**: <https://gitlab.com/meltano/tap-gitlab>
- **Maintainer**: Meltano community
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-gitlab` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-gitlab
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "GitLab".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-gitlab` requires the [configuration](/docs/configuration.html) of the following settings:

- [API URL](#api-url)
- [Private Token](#private-token), unless groups and projects are public
- [Groups](#groups) or [Projects](#projects)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-gitlab` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
    config:
      projects: meltano/meltano meltano/tap-gitlab
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_GITLAB_PRIVATE_TOKEN=my_private_token
```

### API URL

- Name: `api_url`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_API_URL`
- Default: `https://gitlab.com`

GitLab API/instance URL. When an API path is omitted, `/api/v4/` is assumed.

#### How to use

Manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set api_url https://gitlab.example.com

export TAP_GITLAB_API_URL=https://gitlab.example.com
```

### Private Token

- Name: `private_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_PRIVATE_TOKEN`, alias: `GITLAB_API_TOKEN`

GitLab personal access token or other API token.

#### How to get

The process for getting the private token or personal access token is very simple:

<video controls style="max-width: 100%">
  <source src="/screenshots/personal-access-token.mov">
</video>

1. Navigate to your [profile's access tokens](https://gitlab.com/profile/personal_access_tokens).

2. Fill out the personal access token form with the following properties:

- **Name:** meltano-gitlab-tutorial
- **Expires:** _leave blank unless you have a specific reason to expire the token_
- **Scopes:**
  - api

3. Click on `Create personal access token` to submit your request.

4. You should see your token appear at the top of your screen. It should look something like this: `I8vxHsiVAaDnAX3hA`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set private_token <token>

export TAP_GITLAB_PRIVATE_TOKEN=<token>
```

### Groups

- Name: `groups`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_GROUPS`, alias: `GITLAB_API_GROUPS`

This property allows you to scope data that the extractor fetches to only the desired group. The group name can generally be found at the root of a repository's URL. If this is left blank, you have to at least provide a [project](#projects).

Leave empty if you'd like to pull data from a project in a personal user namespace.

For example, `https://www.gitlab.com/meltano/tap-gitlab` has a group of `meltano`.

Multiple group names can be separated using space characters.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set groups "<group1> <group2>"

export TAP_GITLAB_GROUPS="<group1> <group2>"

# For example:
meltano config tap-gitlab set groups meltano
meltano config tap-gitlab set groups "meltano gitlab"

export TAP_GITLAB_GROUPS=meltano
export TAP_GITLAB_GROUPS="meltano gitlab"
```

### Projects

- Name: `projects`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_PROJECTS`, alias: `GITLAB_API_PROJECTS`

This property allows you to scope the project(s) that the extractor fetches.

Leave empty if you've specified one or more [groups](#groups) and would like to pull data from all projects inside these groups.

The format for it is `namespace/project`, where namespace can be a username or group name. Here are a couple examples:

- `meltano/meltano` - The core [Meltano project](https://gitlab.com/meltano/)
- `meltano/tap-gitlab` - The project for the [GitLab Extractor](https://gitlab.com/meltano/tap-gitlab)

Multiple group paths can be separated using space characters.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set projects "<namespace1/project1> <namespace2/project2>"

export TAP_GITLAB_PROJECTS="<namespace1/project1> <namespace2/project2>"

# For example:
meltano config tap-gitlab set projects meltano/meltano
meltano config tap-gitlab set projects "meltano/meltano meltano/tap-gitlab"

export TAP_GITLAB_PROJECTS=meltano/meltano
export TAP_GITLAB_PROJECTS="meltano/meltano meltano/tap-gitlab"
```

### Ultimate License

- Name: `ultimate_license`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_ULTIMATE_LICENSE`, alias: `GITLAB_API_ULTIMATE_LICENSE`
- Default: `false`

Enable to pull in extra data (like Epics, Epic Issues and other entities) only available to GitLab Ultimate and GitLab.com Gold accounts.

The `epics` and `epic_issues` entities cannot be [selected](/docs/integration.html#selecting-entities-and-attributes-for-extraction) unless this setting is enabled.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set ultimate_license true

export TAP_GITLAB_ULTIMATE_LICENSE=true
```

### Fetch Merge Request Commits

- Name: `fetch_merge_request_commits`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_FETCH_MERGE_REQUEST_COMMITS`
- Default: `false`

For each Merge Request, also fetch the MR's commits and create the join table `merge_request_commits` with the Merge Request and related Commit IDs.

This can slow down extraction considerably because of the many API calls required.

The `merge_request_commits` entity cannot be [selected](/docs/integration.html#selecting-entities-and-attributes-for-extraction) unless this setting is enabled.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set fetch_merge_request_commits true

export TAP_GITLAB_FETCH_MERGE_REQUEST_COMMITS=true
```

### Fetch Pipelines Extended

- Name: `fetch_pipelines_extended`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_FETCH_PIPELINES_EXTENDED`
- Default: `false`

For every Pipeline, also fetch extended details of each of these pipelines.

This can slow down extraction considerably because of the many API calls required.

The `pipelines_extended` entity cannot be [selected](/docs/integration.html#selecting-entities-and-attributes-for-extraction) unless this setting is enabled.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set fetch_pipelines_extended true

export TAP_GITLAB_FETCH_PIPELINES_EXTENDED=true
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_GITLAB_START_DATE`, alias: `GITLAB_API_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-gitlab set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_GITLAB_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-gitlab set start_date 2020-10-01T00:00:00Z

export TAP_GITLAB_START_DATE=2020-10-01T00:00:00Z
```
