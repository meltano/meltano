---
sidebar: auto
metaTitle: Extract Data from GitLab
description: Use Meltano to extract raw data from GitLab and insert it into Postgres, Snowflake, and more.
---

# GitLab

The GitLab extractor pulls raw data from GitLab's [REST API](https://docs.gitlab.com/ee/api/README.html) and extracts the following resources from GitLab:

- [Branches](https://docs.gitlab.com/ee/api/branches.html)
- [Commits](https://docs.gitlab.com/ee/api/commits.html)
- [Issues](https://docs.gitlab.com/ee/api/issues.html)
- [Projects](https://docs.gitlab.com/ee/api/projects.html)
- [Project milestones](https://docs.gitlab.com/ee/api/milestones.html)
- [Project Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html)
- [Users](https://docs.gitlab.com/ee/api/users.html)
- [Groups](https://docs.gitlab.com/ee/api/group_milestones.html)
- [Group Milestones](https://docs.gitlab.com/ee/api/users.html)
- [Group and Project members](https://docs.gitlab.com/ee/api/members.html)
- [Tags](https://docs.gitlab.com/ee/api/tags.html)
- [Releases](https://docs.gitlab.com/ee/api/releases/index.html)
- [Group Labels](https://docs.gitlab.com/ee/api/group_labels.html)
- [Project Labels](https://docs.gitlab.com/ee/api/labels.html)
- [Epics](https://docs.gitlab.com/ee/api/epics.html) (only available for GitLab Ultimate and GitLab.com Gold accounts)
- [Epic Issues](https://docs.gitlab.com/ee/api/epic_issues.html) (only available for GitLab Ultimate and GitLab.com Gold accounts)

For more information you can check [the documentation for tap-gitlab](https://gitlab.com/meltano/tap-gitlab).

## GitLab Setup

In order to access your GitLab data, you will need:

- GitLab Instance
- Access Token
- Groups
- Projects
- Start Date

<h3 id="api-url">GitLab Instance</h3>

:::tip Configuration Notes

- `https://gitlab.com` is the default, but if you have a self-hosted GitLab instance [please reach out to us](mailto:hello@meltano.com)

:::

<h3 id="private-token">Access Token</h3>

:::tip Configuration Notes

- Full access to GitLab's API requires a personal access token that will authenticate you with the server

:::

The process for getting the access token is very simple:

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

4. You should see your token appear at the top of your screen.

5. Copy and paste the token into the `Private Token` field. It should look something like this: `I8vxHsiVAaDnAX3hA`

### Groups

:::tip Configuration Notes

- Space separated paths of groups to pull data from.
- Leave empty if you'd like to pull data from projects in a personal user namespace

:::

This property allows you to scope data that the extractor fetches to only the desired group(s). The group name can generally be found at the root of a repository's URL. If this is left blank, you have to at least provide a project.

For example, `https://www.gitlab.com/meltano/tap-gitlab` has a group of `meltano`. This can be confirmed as well by visiting `https://gitlab.com/meltano` and noting the Group ID below the header.

![Group ID verification example](/screenshots/group-header-example.png)

:::tip Configuration options for Groups and projects

- Either groups or projects need to be provided
- Filling in 'groups' but leaving 'projects' empty will sync all the projects for the provided group(s).
- Filling in 'projects' but leaving 'groups' empty will sync the specified projects.
- Filling in 'groups' and 'projects' will sync only the specified projects in those groups.

:::

### Projects

:::tip Configuration Notes

- Space separated paths of projects to pull data from, in `namespace/project` format
- Leave empty if you've specified one or more groups and would like to pull data from all projects inside these groups

:::

This property allows you to scope the project that the service fetches, but it is completely optional. If this is left blank, the extractor will try to fetch all projects that it can grab.

If you want to configure this, the format for it is `group/project`. Here are a couple examples:

- `meltano/meltano` - The core [Meltano project](https://gitlab.com/meltano/)
- `meltano/tap-gitlab` - The project for the [GitLab Extractor](https://gitlab.com/meltano/tap-gitlab)

### Ultimate License

:::tip Configuration Notes

- Pull in extra data (like Epics, Epic Issues and other entities) only available to GitLab Ultimate and GitLab.com Gold accounts.

:::

### Start Date

:::tip Configuration Notes

- Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.

## Meltano Setup

### Prerequisites

- [Running instance of Meltano](/docs/getting-started.html)

### Configure the Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and GitLab Extractor highlighted](/images/gitlab-tutorial/01-gitlab-extractor-selection.png)

Let's install `tap-gitlab` by clicking on the `Install` button inside its card.

On the configuration modal we want to enter the Private Token the GitLab extractor will use to connect to GitLab, the Groups and Projects we are going to extract from and the Start Date we want the extracted data set to start from.

![Screenshot of GitLab Extractor Configuration](/images/gitlab-tutorial/02-gitlab-configuration.png)

::: tip

**Ready to do more with data from GitLab?**

Check out our [GitLab API + Postgres tutorial](/tutorials/gitlab-and-postgres.html) to learn how you can create an analytics database from within Meltano, and start analyzing your GitLab data.

:::

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
1. Run the following command:

```bash
meltano add extractor tap-gitlab
```

If you are successful, you should see `Added and installed extractors 'tap-gitlab'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

Required:

```bash
export GITLAB_API_TOKEN="private access token"
export GITLAB_API_GROUPS="myorg mygroup"
export GITLAB_API_PROJECTS="myorg/repo-a myorg/repo-b"
export GITLAB_API_START_DATE="YYYY-MM-DDTHH:MM:SSZ" # e.g. 2019-10-31T00:00:00Z
```

Optional:

```bash
export GITLAB_API_ULTIMATE_LICENSE="true"
```

If `ultimate_license` is true (defaults to false), then the GitLab account used has access to the GitLab Ultimate or GitLab.com Gold features. It will enable fetching Epics, Epic Issues and other entities available for GitLab Ultimate and GitLab.com Gold accounts.

Check the [README](https://gitlab.com/meltano/tap-gitlab) for details.
