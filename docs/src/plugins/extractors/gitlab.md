---
sidebar: auto
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
- [Epics](https://docs.gitlab.com/ee/api/epics.html) (only available for Gitlab Ultimate and Gitlab.com Gold accounts)
- [Epic Issues](https://docs.gitlab.com/ee/api/epic_issues.html) (only available for Gitlab Ultimate and Gitlab.com Gold accounts)

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

3. Get your GitLab access token
   - Login to your GitLab account
   - Navigate to your profile page
   - Create an access token

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export GITLAB_API_TOKEN="access token from step 3"
export GITLAB_API_GROUPS="myorg mygroup"
export GITLAB_API_PROJECTS="myorg/repo-a myorg-repo-b"
# The date uses ISO-8601 and supports time if desired
export GITLAB_API_START_DATE="YYYY-MM-DD"
export GITLAB_API_ULTIMATE_LICENSE="true"
```

If `ultimate_license` is true (defaults to false), then the GitLab account used has access to the Gitlab Ultimate or Gitlab.com Gold features. It will enable fetching Epics, Epic Issues and other entities available for Gitlab Ultimate and Gitlab.com Gold accounts.

::: warning

- Either groups or projects need to be provided
- Filling in 'groups' but leaving 'projects' empty will sync all group projects.
- Filling in 'projects' but leaving 'groups' empty will sync selected projects.
- Filling in 'groups' and 'projects' will sync selected projects of those groups.

Currently, groups don't have a date field which can be tracked
:::
