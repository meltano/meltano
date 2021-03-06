---
sidebarDepth: 2
---

# Engineering Handbook

## Subresources

- [MeltanoData Guide](/handbook/engineering/meltanodata-guide/)

## Issue tracker best practices

### Milestones

Every open issue should have a [milestone](https://gitlab.com/groups/meltano/-/milestones).
If something we want to happen eventually is not a priority yet, use `Backlog`.
If we don't want it to happen, close the issue.

Once an issue becomes a priority, set a sprint milestone (identified by the Friday of the week in question),
even if it's still weeks away and may end up being moved.

New sprint milestones are created about 6 weeks in advance as part of preparation for the weekly kickoff meeting.

### Labels

Every open issue _with a sprint milestone_ should have a `flow` label:

- `flow::Triage` : On our mind for this milestone, but likely to be moved to a subsequent week. If there's room in the week in question, can be moved to `flow::To Do`
- `flow::To Do`: Something we intend to do during the week in question
- `flow::Doing`: Currently being worked on
- `flow::Blocked`: Blocked by some other issue
- `flow::Review`: Currently in review

When possible, an issue should have a label indicating its type:
- `bug`
- `feature requests`
- `Discussion`
- `Exploration`
- `Community Support`

If appropriate, an issue should have a stage label (one of the letters in "meltano"):
- `Model`
- `Extract`
- `Load`
- `Transform`
- `Analyze`
- `Notebook` (currently unused)
- `Orchestrate`

Other labels:
- `CLI` or `UI` for issues specifically concerning the CLI or UI
- `Documentation` for new or updated documentation
- `Accepting Merge Requests` for issues that are ready to be picked up by a community contributor
- `integrations` for issues relating to integrations with other open source data tools, typically as plugins
- `Configuration` for issues relating to configuration
- `Plugin Management` for issues relating to plugin management

New labels can be created as appropriate and should be documented them here.

### Epics

When appropriate, house an issue under an existing epic: <https://gitlab.com/groups/meltano/-/epics>

New epics can be created for topics or efforts that will take multiple issues over multiple sprints.
## Triage process

::: warning
This process is not currently in use. It will be updated when we adopt a new process appropriate for the current team.
:::

The `flow::Triage` label is used on issues that need product/prioritization triage by the Product Manager (Danielle), or engineering/assignment triage by the Engineering Lead (Douwe).
After they've been triaged, they'll have a milestone (other than `Backlog`), an assignee, and the `flow::To Do` label.

If you come across something that needs fixing:

1. Create an issue describing the problem.
2. If it's not obvious, justify how it relates to our persona and how it contributes to MAUI.
3. Then:

    - If it's more urgent (has a higher impact on MAUI) than other things you've been assigned, assign it to yourself to work on later the same week:

      ```md
      /milestone %<current milestone>
      /label ~"flow::To Do"
      /reassign @<yourself>
      /cc @DouweM
      ```

    - If it's urgent, but you're not sure who should work on it, assign it to Douwe to triage:

      ```md
      /milestone %<current milestone>
      /label ~"flow::Triage"
      /reassign @DouweM
      ```

    - If it's _not_ urgent or you're unsure whether it's something we should do at all, assign it to Danielle to triage:

      ```md
      /milestone %“Backlog" or %<next milestone>
      /label ~"flow::Triage"
      /reassign @dmor
      ```

## Useful issue boards

- [Development Flow](https://gitlab.com/groups/meltano/-/boards/536761), with a column for each `flow::` label. Don't forget to filter by milestone, and/or assignee!
- [Team Assignments](https://gitlab.com/groups/meltano/-/boards/1402405), with a column for each team member. Don't forget to filter by milestone!
- [Current Milestone](https://gitlab.com/groups/meltano/-/boards/1288307), with a column for each `flow::` label _and_ each team member.
- [Next Milestone](https://gitlab.com/groups/meltano/-/boards/1158410), with a column for each `flow::` label _and_ each team member.

## Release Process

### Schedule

We aim to release every Monday and Thursday, unless there are no [unreleased changes](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md#unreleased).

### Versioning

Regular releases get a minor version bump (`1.1.0` -> `1.2.0`).
Releases that only address regressions introduced in the most recent release get a patch version bump (`1.2.0` -> `1.2.1`).

We may want to strictly adhere to [semver](https://semver.org/) at some point.

### Workflow

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.

1. Ensure you have the latest `master` branch locally before continuing.

   ```bash
   cd meltano

   git checkout master
   git pull
   ```

1. Install the latest versions of all release toolchain dependencies.

   ```bash
   poetry install
   ```

2. Execute the commands below:

   ```bash
   # create and checkout the `release-next` branch from `origin/master`
   git checkout -B release-next origin/master

   # view changelog (verify changes made match changes logged)
   poetry run changelog view

   # after the changelog has been validated, tag the release
   make type=minor release
   # if this is a patch release:
   # make type=patch release

   # ensure the tag once the tag has been created, check the version we just bumped to: e.g. `0.22.0` => `0.23.0`.
   git describe --tags --abbrev=0

   # push the tag upstream to trigger the release pipeline
   git push origin $(git describe --tags --abbrev=0)

   # push the release branch to merge the new version, then create a merge request
   git push origin release-next
   ```

1. Create a merge request from `release-next` targeting `master` and use the `release` template.
2. Add the pipeline link (the one that does the actual deployment) to the merge request. Go to the commit's pipelines tab and select the one that has the **publish** stage.
3. Make sure to check `delete the source branch when the changes are merged`.
4. Follow remaining tasks that are part of the `release` merge request template

## Demo Day

::: warning
This process is not currently in use. It will be updated when we adopt a new process appropriate for the current team.
:::

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

## Outages & escalation

Both https://www.meltano.com and https://meltano.meltanodata.com are automatically monitored using Pingdom, with notifications of downtime posted to:
- the #meltano Slack channel,
- Zendesk, through our `hello@` email address, and
- Douwe, by email and SMS.

Other `*.meltanodata.com` instances are not currently monitored.

When any instance managed by us is reported to be down, through Pingdom or any other means, resolving this becomes the team's top priority.
