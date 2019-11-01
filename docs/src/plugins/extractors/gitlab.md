---
sidebar: auto
metaTitle: Extract Data from GitLab
description: Use Meltano to extract raw data from GitLab and insert it into Postgres, Snowflake, and more.
---

# GitLab

`tap-gitlab` pulls raw data from GitLab's [REST API](https://docs.gitlab.com/ee/api/README.html) and extracts the following resources from GitLab:

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

It incrementally pulls data based on the input state and then outputs the schema for each resource and the extracted data. For more information you can check [the documentation for tap-gitlab](https://gitlab.com/meltano/tap-gitlab).

## Info

- **Data Source**: [GitLab's REST API](https://docs.gitlab.com/ee/api/README.html)
- **Repository**: [https://gitlab.com/meltano/tap-gitlab](https://gitlab.com/meltano/tap-gitlab)

## Install

1. Navigate to your Meltano project in the terminal
1. Run the following command:

```bash
meltano add extractor tap-gitlab
```

If you are successful, you should see `Added and installed extractors 'tap-gitlab'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export GITLAB_API_TOKEN="private access token"
export GITLAB_API_GROUPS="myorg mygroup"
export GITLAB_API_PROJECTS="myorg/repo-a myorg-repo-b"
# The date uses ISO-8601 and supports time if desired
export GITLAB_API_START_DATE="YYYY-MM-DDTHH:MM:SSZ" # e.g. 2019-10-31T00:00:00Z
export GITLAB_API_ULTIMATE_LICENSE="true"
```

If `ultimate_license` is true (defaults to false), then the GitLab account used has access to the Gitlab Ultimate or Gitlab.com Gold features. It will enable fetching Epics, Epic Issues and other entities available for Gitlab Ultimate and Gitlab.com Gold accounts.

::: warning

- Either groups or projects need to be provided
- Filling in 'groups' but leaving 'projects' empty will sync all the projects for the provided group(s).
- Filling in 'projects' but leaving 'groups' empty will sync selected projects.
- Filling in 'groups' and 'projects' will sync selected projects of those groups.

:::

The following sections explain how to obtain and fill the rest of the required properties.

### GitLab API Token

In order to access GitLab's API to fetch data, we must get a personal access token that will authenticate you with the server. This is very simple to do:

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

5. Copy and paste the token into the `GITLAB_API_TOKEN` property. It should look something like this: `I8vxHsiVAaDnAX3hA`

:::tip Advanced Use Case
You can set the `GITLAB_API_TOKEN` to " " (a single space) if you want to extract data from a public project and don't have an account for GitLab.

But you are not going to be able to fetch everything supported by the GitLab Extractor: members, milestones, labels and other entities that we may reference in this Tutorial require an authenticated user to be fetched.
:::

### Projects

This property allows you to scope the project that the service fetches, but it is completely optional. If this is left blank, the extractor will try to fetch all projects that it can grab.

If you want to configure this, the format for it is `group/project`. Here are a couple examples:

- `meltano/meltano` - The core [Meltano project](https://gitlab.com/meltano/)
- `meltano/tap-gitlab` - The project for the [GitLab Extractor](https://gitlab.com/meltano/tap-gitlab)

### Groups

This property allows you to scope data that the extractor fetches to only the desired group(s). The group name can generally be found at the root of a repository's URL. If this is left blank, you have to at least provide a project.

For example, `https://www.gitlab.com/meltano/tap-gitlab` has a group of `Meltano`. This can be confirmed as well by visiting `https://gitlab.com/meltano` and noting the Group ID below the header.

![Group ID verification example](/screenshots/group-header-example.png)

### Start Date

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.
