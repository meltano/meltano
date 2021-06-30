---
sidebarDepth: 2
---

# Engineering Handbook

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
- `Bug`
- `Feature Request`
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

Singer related labels:
- `Singer Ecosystem` for general Singer related issues
- `MeltanoHub - Singer`
- `Singer SDK`

Other labels:
- `CLI` or `UI` for issues specifically concerning the CLI or UI
- `Documentation` for new or updated documentation
- `Accepting Merge Requests` for issues that are ready to be picked up by a community contributor
- `Integrations` for issues relating to integrations with other open source data tools, typically as plugins
- `Configuration` for issues relating to configuration
- `Plugin Management` for issues relating to plugin management

New labels can be created as appropriate at the Group Level and should be documented them here.

### Epics

When appropriate, house an issue under an existing epic: <https://gitlab.com/groups/meltano/-/epics>

New epics can be created for topics or efforts that will take multiple issues over multiple sprints.

## Code review

All non-trivial merge requests should be reviewed and merged by someone other than the author.
A merge request that touches code is never trivial, but one that fixes a typo in the documentation probably is.

All team members are expected to review community contributions, but these can only be merged by an expert on the part of the code base in question.
Right now, Douwe is the only expert.

As experts catch issues in MRs that the original reviewers did not,
we will update this section and the [Contributor Guide](/docs/contributor-guide.md#reviews),
and reviewers will learn new things to look out for until they catch (almost) everything the expert would,
at which points they will be experts themselves.

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

3. Using the link from the `git push` output, create a merge request from `release-next` targeting `master` and use the `release` template. Follow all tasks that are part of the `release` merge request template.

## Zoom

For community calls, use one of the following background in Zoom depending on whether you mirror your video or not.

Note that if you mirror your video then the image will look backwards on your screen, but to others in the call it will look correct.

![Meltano Background](/images/zoom-backgrounds/meltano-background.png)

Add it by doing the following:

* Download the file and store it on your computer
* Navigate to Preferences
* Click Background & Filters
* Within Virtual Backgrounds, click the `+` icon and add the file

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

## Office Hours

Recurring office hours are available for Meltano community members to discuss our roadmap, debug issues, and ask questions. For schedules and meeting links, please check our [#office-hours](https://meltano.slack.com/archives/C01QS0RV78D) channel in <SlackChannelLink>Slack</SlackChannelLink>.

### Office Hours: Workflow

#### Prepping the week ahead

- Within the week or two leading up to the office hours, look out for at least one or two community members and corresponding topics which can benefit from synchronous communication.
- Prep a list of contributor names so we can call them out during the session as time allows. (Use a dedicated slide with their names or aliases if warranted.)
- Timebox rotating topics and set expectations ahead of time in the slides: e.g. 15 minutes for dedicated topic, 45 minutes for questions, debugging, AMA, etc.

#### Day before the meeting:

- Slack:
    - Post reminder to #office-hours
    - Share to #announcements
- Tweet:
    - Draft a short memo for the Tweet text. Post should come from the brand account with office hours link and time.
    - Schedule Tweet for 30 minutes ahead of session.
    - RT from personal accounts.

#### 10 Minutes before Meeting Time:

1. Launch zoom meeting room as usual.
2. Immediately start the YouTube auth flow (5-10 minutes ahead of the stream start):
    1. From the "More" or "..." menu, select "Live on Youtube".
    2. When asked which account, select your `@meltano` account.
    3. When asked which brand account, select the `Meltano` brand.
    4. When asked for a stream title, accept the default title `Meltano Office Hours`. (We'll update this title later.)
    5. Wait on this screen until the designated meeting time and you are ready to hit 'Go Live!'
    6. Optionally, in Zoom you may copy the livestream link and paste into Slack `#office-hours` channel.

#### During the Office Hours session

- When discussions are in progress, drop the screenshare in order to give participants more face time.
- Be aware that the owner's view layout (gallery or otherwise) also changes the view for others.
- Share any relevant links in the zoom chat.

#### After the livestream session ends

1. Log into the YouTube account, locate the livestream and select the "Edit" option.
2. Update the video title with the date of the session, e.g. `Meltano Office Hours Livestream on YYYY-MM-DD`
3. Update the video front image with a screenshot of the deck.
4. Generate list of timestamps for each significant topic.
5. Update the topic features + timestamps within the YouTube video description.
6. Add a link within the video description to the `#office-hours` channel in slack.
7. Note: Although YouTube does allow editing in the website, this feature is not available until
   several hours after the recording, and video edits might take up to several hours to apply.

#### Preventing and responding to accidental secrets leakage

As a standard practice, we should remind community members whenever they are sharing their screens: `"As a
reminder, this session is being livestreamed and recorded. We recommend closing any
credential files or other sensitive documents prior to starting the screenshare."`

And, although we should make a reasonable attempt to prevent confidential information on screenshare, these
things do accasionally happen. In those cases, our goal is to mitigate exposure such to significantly reduce the
exposure and reduce the chances that a malicious actor takes advantage of the vulnerability.
Towards this end, the following actions should be taken as soon as anyone on the team realizes there were
credentials/secrets exposed:

1. Immediately reach out on slack to whoever was sharing their screen and advise them to rotate their credentials
   as soon as possible.
    - You can also refer them to this page. Since we don't know if they are watching slack,
      it is a good idea to ask them for confirmation that they received your message. If they do not reply,
      kindly call out in Zoom chat that they should check their Slack messages.
    - Note: because users who were watching in the stream could technically pause or screenshot the leaked creds,
      this guidance to reset credentials should apply regardless of the duration of time that the credentials
      were onscreen.
2. Immediately after notifying the presenter of the issue, go to our
   [Meltano YouTube channel](https://studio.youtube.com/channel/UCmp7zJAZEC7I_n9BEydH8XQ/videos/upload) ->
   "Manage Content" and locate the in-progress livestream.
    - Change the privacy settings on the livestream to from 'Public' to 'Private'.
    - Optionally, post to the slack channel that the livestream is temporarily down and users can rejoin with the
      Zoom link.
3. After the livestream ends:
    1. Wait up to 24 hours for YouTube to complete processing _OR_ download the raw video so that you can editing
       locally.
    2. Once video is processed, you will be able to use YouTube's content editor to clip out the frames which
       contained the onscreen secrets exposure.
    3. Once the video is edited, you may need to wait again for YouTube to finish processing the edited video.
    4. After confirming the edit by watching the video you can re-share as "Public".
    5. If you downloaded and edited the video locally, you will need to provide a new YouTube link. If you edited
       directly, the old links will still work once the video is made "Public" again.

* _Note: if one person is leading the meeting and multiple team members are present, whoever is not presenting should take steps (1) and (2) above, while the other team member continues to lead the remainder of the session._

## Outages & escalation

Both https://www.meltano.com and https://meltano.meltanodata.com are automatically monitored using Pingdom, with notifications of downtime posted to:
- Zendesk, through our `hello@` email address, and
- Douwe, by email and SMS.

Other `*.meltanodata.com` instances are not currently monitored.

When any instance managed by us is reported to be down, through Pingdom or any other means, resolving this becomes the team's top priority.

## GitHub Mirrors

We mirror the three main Meltano repositories (meltano/sdk/hub) from GitLab to GitHub. This is managed via the "Mirroring repositories" section with the Settings of the GitLab repository. The push was created using Taylor's personal GitHub account (tayloramurphy) with a personal access token made just for the use case. This was tracked in [this issue](https://gitlab.com/meltano/meta/-/issues/55).
