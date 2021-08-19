[//]: # (NOTE: This Release template is for Admin-Use only. If you've reached this template in error, please select another template from the list.)

## Evergreen Releases - Prep Steps:

An `Evergreen` release process means we are _always_ releasing. We open a new release ticket as soon as we've completed the prior release. (It's therefore the final step in this checklist.)

## "Evergreen Prep" Checklist

- [x] Open this Issue
- [ ] Indicate the version to be released here in the issue's title and here: `vX.Y.Z`
    - If the release number changes (from minor to major or patch, for instance), update the version here and in the issue description.
- [ ] Provide the _planned_ release date: `yyyy-mm-dd` 

### Release Readiness Checklist:

`Engineering` team, the Monday prior to the release:

1. [ ] Ensure all already-merged commits since the last release have changelog entries (excepting non-user-impacting commits, such as docs fixes).
2. [ ] Create a comment in this issue with pending-but-not-merged MRs potentially shipping.
    - Otherwise a comment that all known merge candidates are already merged.
3. [ ] Link issues to this issue which have already merged, or are expected to merge.

### Release Checklist

`Marketing` and `Product`, on the day prior to the release:

Leveraging the combination of linked issues

1. [ ] Review the changelog for [grokability](https://en.wikipedia.org/wiki/Grok), merging an update for clarity/readability/typos if needed.
2. [ ] Create summary readouts for any planned blog posts, optionally requesting clarification or additional exposition in the `#engineering-team` channel.
3. [ ] Unlink any 'slipped' issues which are not being included in this release.

Rotating `assignee`, on the morning of the release:

1. [ ] Changelog updates and version bump:
    1. [ ] Create a new branch named `release/vX.Y.Z` and a corresponding MR.
    2. An automated pipeline (linked to the branch prefix `release/v*`) will
    automatically bump the version and flush the changelog.
        - [ ] Check this box to confirm the automated changelog flush and version bump are complete.
    3. [ ] Review the changelog, committing an update for clarity/readability/typos if needed.
    4. [ ] Compare against `main` branch [commit history](https://gitlab.com/meltano/meltano/-/commits/main) and add any significant user-impacting updates, excluding docs.
    5. [ ] Open the Changelog in preview mode, mouse over each link and ensure tooltip descriptions match the resolved issue. Check contributor profile links to make sure they are correct.
    6. [ ] Merge the resulting MR to `main` with the merge commit message `Release vX.Y.Z`
2. [ ] Cut a release
       - [ ] Cut a release tag with the name `vX.Y.Z` and description `Release vX.Y.Z`
       - In response to new tag creation, these steps are performed automatically in Gitlab pipelines:
           - Abort if tag `vX.Y.Z` does not match output from `poetry version --short`
           - [ ] Publish to [PyPi](https://pypi.org/project/meltano/#history)
           - [ ] Publish to [Docker](https://hub.docker.com/r/meltano/meltano)
3. [ ] Open the next `Release` issue, assign as appropriate, and provide that link here: `___`

### Announcements, Marketing, and Promotion

`Marketing` @emily or `Product` team:

1. [ ] Post-release announcement steps:
    1. [ ] Post announcement to Meltano slack: `#announcements`
    2. Copy-paste to:
       - [ ] `Singer` slack: `#meltano`
       - [ ] `dbt` slack: `#tools-meltano`
    3. [ ] Blog post
    4. [ ] Tweet the blog post

----------------

/label ~Release ~"flow::Doing"
