[//]: # (NOTE: This Release template is for Admin-Use only. If you've reached this template in error, please select another template from the list.)

## Evergreen Releases - Prep Steps

An `Evergreen` release process means we are _always_ releasing.

## "Evergreen Prep" Checklist

- [x] Open this Issue
- [ ] Indicate the version to be released in the issue's title: `Release vX.Y.Z`
  - If the release number changes (from minor to major or patch, for instance), update the version in the issue title.

### Readiness Checklist

`Engineering` team, to get ready for the upcoming release:

1. [ ] Ensure any [already-merged commits](https://gitlab.com/meltano/meltano/-/commits/master) since the last release have [Changelog](https://gitlab.com/meltano/meltano/-/blob/master/CHANGELOG.md) entries (excepting non-user-impacting commits, such as docs fixes).
2. [ ] Create a comment in the `#engineering-team` slack channel with pending-but-not-merged MRs, potentially shipping. (Aka, the "burndown" list.)
    - Otherwise a comment that all known merge candidates are already merged.
3. [ ] Create or link to a summary of MRs merged and/or expected in the `#marketing` Slack channel, with an `@channel` mention.

### Release Checklist

Rotating `assignee`, on the morning of the release:

1. [ ] Changelog updates and version bump:
    1. [ ] Check the [pending MRs](https://gitlab.com/meltano/meltano/-/merge_requests?sort=updated_desc) to make sure nothing expected is still waiting to be merged.
    2. [ ] Create a new branch named `release/vX.Y.Z` and a corresponding MR with the `Release` MR template.
    3. An auto-generated commit will immediately and automatically bump the version and flush the changelog.
        - The CI pipeline will take approximately 45 minutes. Watch for errors (esp. `tap-gitlab` sample project failures).
        - [ ] When the option becomes available, manually trigger the `publish_trigger` job in the CI pipeline that was triggered by the auto-commit with the version bump.
    4. In response to triggering the `publish_trigger` job, these steps will be performed automatically:
        1. Abort if release branch name `release/vX.Y.Z` does not match output from `poetry version --short`
        2. Publish to PyPi <!-- Meltano-only: and Docker -->.
    5. Validate publish once the pipeline finishes. (While the process is running, you can continue with next steps, such as changelog grooming.)
        1. [ ] Check this box when the release [pipeline](https://gitlab.com/meltano/meltano/-/pipelines) has fully completed, including the manually triggered publish steps.
        2. [ ] Check this box when [PyPi publish](https://pypi.org/project/meltano/#history) is confirmed. (Will also be posted to `#activity-feed` in Slack.)
        <!-- Meltano-only: 5. [ ] Check this box when [Docker publish]() is confirmed. -->
2. [ ] ~~[Cut a release tag](https://gitlab.com/meltano/meltano/-/tags/new) from your `release/vX.Y.Z` branch _(not from `main`)_ named `vX.Y.Z` with Message=`Release vX.Y.Z`~~ (Skipping for now.)
3. [ ] Merge the release MR, resolving changelog conflicts if necessary.

### Changelog Grooming Checklist

_These can be performed in parallel to the release pipeline executing._

1. [ ] Compare the [changelog](https://gitlab.com/meltano/meltano/-/blob/master/CHANGELOG.md) against the `main` branch [commit history](https://gitlab.com/meltano/meltano/-/commits/master) and add any significant user-impacting updates (excluding docs and website updates, for instance).
2. [ ] Review the changelog for readability and typos, committing fixes or updates if needed.
3. [ ] Final changelog review:
   - Open the changelog in preview mode, mouse over each link and ensure tooltip descriptions match the resolved issue.
   - Check contributor profile links to make sure they are correct.
4. [ ] Merge the resulting MR to `main` with the merge commit message `Release vX.Y.Z`

### Announcements, Marketing, and Promotion

`Marketing` or `Product` team:

1. [ ] Post-release announcement steps:
   1. [ ] Post announcement to Meltano slack: `#announcements`
   <!-- SDK only: 2. [ ] Cross-post (share) to `#sdk` -->
   1. Copy-paste to:
      - [ ] `Singer` slack: `#meltano` <!-- SDK only: `#singer-sdk` -->
      - [ ] `dbt` slack: `#tools-meltano`
   2. [ ] Blog post
   3. [ ] Tweet the blog post

----------------
