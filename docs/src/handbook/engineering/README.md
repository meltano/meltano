---
sidebarDepth: 2
---

# Engineering Handbook

## Subresources

- [MeltanoData Guide](/handbook/engineering/meltanodata-guide/)

## Triage process

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

Every Monday, we do a minor release (1.x) that is accompanied by a blog post.

Additionally, we do a patch (1.x.y) or minor release every Thursday, to not leave users waiting to see improvements longer than necessary.

### Versioning

Meltano uses [semver](https://semver.org/) as its version number scheme.

### Prerequisites

Ensure you have the latest `master` branch locally before continuing.

```shell
git fetch origin
```

### Workflow

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.

1. Meltano has a number of dependencies for the release toolchain that are required when performing a release. If you haven't already, please navigate to your meltano installation and run the following command to install all development dependencies:

   ```shell
   # activate your virtualenv
   source ./venv/bin/activate

   # pip3 install all the development dependencies
   pip3 install .[dev]
   ```

2. Execute the commands below:

   ```shell
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

**Tip:** Releasing a hotfix? You can use `make type=patch release` to force a patch release. This is useful when we need to release hotfixes.

1. Create a merge request from `release-next` targeting `master` and use the `release` template.
2. Add the pipeline link (the one that does the actual deployment) to the merge request. Go to the commit's pipelines tab and select the one that has the **publish** stage.
3. Make sure to check `delete the source branch when the changes are merged`.
4. When the **publish** pipeline succeeds, the release is publicly available on [PyPI](https://pypi.org/project/meltano/).
5. Follow the [Digital Ocean publish process](#digitalocean-marketplace)
6. Upgrade all MeltanoData.com instances by running the [`meltano-upgrade.yml` Ansible playbook](./meltanodata-guide/controller-node.html#meltano-upgrade-yml)
7. Verify that the full end-to-end flow can be completed successfully on <https://meltano.meltanodata.com>.

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

## DigitalOcean Marketplace

Meltano is deployed and available as a [DigitalOcean Marketplace 1-Click install](https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322).

### Find the snapshot name

**Tip:** The _digitalocean_marketplace_ job is only available on pipelines running off `tags`.

1. The snapshot string should be available under `meltano-<timestamp>` on DigitalOcean, which you will find at the bottom of the _digitalocean_marketplace_ job. Take note of this snapshot string as you'll use it in the next step.

### Update the DigitalOcean listing

Then, head to the DigitalOcean vendor portal at <https://marketplace.digitalocean.com/vendorportal> to edit the Meltano listing.

**Tip:** Don't see the Meltano listing? You'll have to be granted access to the DigitalOcean vendor portal. Please ask your manager for access.

1. Once inside the listing, update the following entries:
   - **Version** to the latest Meltano version
   - **System Image** to the new image (match the aforementioned snapshot string)
   - **Meltano Package Version** inside the _Software Included Entry_
2. Submit it for review to finish the process.

## Outages & escalation

Both https://www.meltano.com and https://meltano.meltanodata.com are automatically monitored using Pingdom, with notifications of downtime posted to:
- the #meltano Slack channel,
- Zendesk, through our `hello@` email address, and
- Douwe, by email and SMS.

Other `*.meltanodata.com` instances are not currently monitored.

When any instance managed by us is reported to be down, through Pingdom or any other means, resolving this becomes the team's top priority.
