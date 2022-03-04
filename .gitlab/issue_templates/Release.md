[//]: # (NOTE: This Release template is for Admin-Use only. If you've reached this template in error, please select another template from the list.)

## Evergreen Releases - Prep Steps:

An `Evergreen` release process means we are _always_ releasing. We open a new release ticket as soon as we've completed the prior release. (It's therefore the final step in this checklist.)

## "Evergreen Prep" Checklist

- [x] Open this Issue
- [ ] Indicate the version to be released here in the issue's title `Release vX.Y.Z`
    - If the release number changes (from minor to major or patch, for instance), update the version here and in the issue description.

### Readiness Checklist:

`Engineering` team, to get ready for the upcoming release:

1. [ ] Ensure any [already-merged commits](https://gitlab.com/meltano/meltano/-/commits/master) since the last release have [Changelog](https://gitlab.com/meltano/meltano/-/blob/master/CHANGELOG.md) entries (excepting non-user-impacting commits, such as docs fixes).
2. [ ] Create a comment in the `#engineering-team` slack channel with pending-but-not-merged MRs, potentially shipping. (Aka, the "burndown" list.)
    - Otherwise a comment that all known merge candidates are already merged.
3. [ ] Create or link to a summary of MRs merged and/or expected in the `#marketing` Slack channel, with an `@channel` mention.

### Release Checklist

Rotating `assignee`, on the morning of the release:

1. [ ] Changelog updates and version bump:
    1. [ ] Check the [pending MRs](https://gitlab.com/meltano/meltano/-/merge_requests?sort=updated_desc) to make sure nothing expected is still waiting to be merged.
    2. [ ] Create a [new branch](https://gitlab.com/meltano/meltano/-/branches/new) named `release/vX.Y.Z` and a corresponding MR with the `Release` MR template.
    3. An automated pipeline (linked to the branch prefix `release/v*`) will
    immediately and automatically bump the version and flush the changelog.
        - [ ] Check this box to confirm the automated changelog flush and version bump are correct.
        - You _do not_ need to wait for the CI pipeline. (An identical CI pipeline is already included in the below.)
2. [ ] [Cut a release tag](https://gitlab.com/meltano/meltano/-/tags/new) from your `release/vX.Y.Z` branch _(not from `main`)_ named `vX.Y.Z` with Message=`Release vX.Y.Z`
    1. In response to new tag creation, these steps are performed automatically in Gitlab pipelines:
        1. Abort if tag `vX.Y.Z` does not match output from `poetry version --short`
        2. Test _everything_.
        3. Publish to PyPi <!-- Meltano-only: and Docker -->.
    2. Validate publish once the pipeline finishes. (While the process is running, you can continue with next steps, such as changelog grooming.)
        1. [ ] Check this box when the tag's [pipeline](https://gitlab.com/meltano/meltano/-/pipelines) has completed (eta 40-60 minutes).
        2. [ ] Check this box when [PyPi publish](https://pypi.org/project/meltano/#history) is confirmed.
        <!-- Meltano-only: 5. [ ] Check this box when [Docker publish]() is confirmed. -->
3. Groom the changelog:
    1. [ ] Compare the [Changelog](https://gitlab.com/meltano/meltano/-/blob/master/CHANGELOG.md) against the `main` branch [commit history](https://gitlab.com/meltano/meltano/-/commits/master) and add any significant user-impacting updates (excluding docs and website updates, for instance).
    3. [ ] Review the Changelog for readability and typoes, committing fixes or updates if needed.
    2. [ ] Final changelog review:
        - Open the Changelog in preview mode, mouse over each link and ensure tooltip descriptions match the resolved issue.
        - Check contributor profile links to make sure they are correct.
    3. [ ] Merge the resulting MR to `main` with the merge commit message `Release vX.Y.Z`
    4. [ ] [Open the next `Release` issue](https://gitlab.com/meltano/meltano/-/issues/new?issuable_template=Release&issue[title]=Release%20vX.Y.Z&issue[issue_type]=issue).

### Announcements, Marketing, and Promotion

`Marketing` or `Product` team:

1. [ ] Post-release announcement steps:
    1. [ ] Post announcement to Meltano slack: `#announcements`
    <!-- SDK only: 2. [ ] Cross-post (share) to `#sdk` -->
    3. Copy-paste to:
       - [ ] `Singer` slack: `#meltano` <!-- SDK only: `#singer-sdk` -->
       - [ ] `dbt` slack: `#tools-meltano`
    4. [ ] Blog post
    5. [ ] Tweet the blog post

----------------
