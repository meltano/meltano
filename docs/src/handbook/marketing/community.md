---
title: "Community"
sidebarDepth: 2
---

# Community

## Regular Community Events & Livestreams

### Office Hours

Recurring office hours are available for Meltano community members to discuss our roadmap, debug issues, and ask questions. For schedules and meeting links, please check our [#office-hours](https://meltano.slack.com/archives/C01QS0RV78D) channel in <SlackChannelLink>Slack</SlackChannelLink>.

#### Office Hours Workflow

- Create an issue on the Marketing General project using the Office Hours issue template. The template will walk you through the steps to host office hours and provides a timeline for making announcements across various channels such as Slack and Twitter.

#### Sourcing Contributors

- Within the week or two leading up to the office hours, look out for at least one or two community members and corresponding topics which can benefit from synchronous communication.
- Prep a list of contributor names so we can call them out during the session as time allows. (Use a dedicated slide with their names or aliases if warranted.)
- Timebox rotating topics and set expectations ahead of time in the slides: e.g. 15 minutes for dedicated topic, 45 minutes for questions, debugging, AMA, etc.

#### Best Practices

- When discussions are in progress, drop the screenshare in order to give participants more face time.
- Be aware that the owner's view layout (gallery or otherwise) also changes the view for others.
- Share any relevant links in the zoom chat.

### Demo Day

For each demo day, we need to ensure that the following process is followed:

#### Demo Day: Setup

1. Document list of features to demo
2. Document order of people demoing
3. Ensure every person demoing has proper display size (i.e., font sizes, zoomed in enough, etc.)
   - Font size at least 20px
   - Browser zoom at least 125%

#### Demo Day: Workflow

1. Record each meeting with Zoom
2. Generate list of timestamps for each featured demo
3. Generate list of features (from Setup section) paired with timestamps
4. Upload recording to YouTube
5. Add features + timestamps to YouTube description

### Streaming From Zoom to YouTube

1. Launch zoom meeting room as usual.
2. Immediately start the YouTube auth flow (5-10 minutes ahead of the stream start):
    1. From the "More" or "..." menu, select "Live on Youtube".
    2. When asked which account, select your `@meltano` account.
    3. When asked which brand account, select the `Meltano` brand.
    4. When asked for a stream title, accept the default title `Meltano Office Hours`. (We'll update this title later.)
    5. Wait on this screen until the designated meeting time and you are ready to hit 'Go Live!'
    6. Optionally, in Zoom you may copy the livestream link and paste into Slack `#office-hours` channel.

#### After the livestream session ends

1. Log into the YouTube account, locate the livestream and select the "Edit" option.
2. Update the video title with the date of the session, e.g. `Meltano Office Hours - YYYY-MM-DD`
3. Update the video front image with a screenshot of the deck.
4. Generate list of timestamps for each significant topic.
5. Update the topic features + timestamps within the YouTube video description.
6. Add a link within the video description to the `#office-hours` channel in slack.
7. Note: Although YouTube does allow editing in the website, this feature is not available until
   several hours after the recording, and video edits might take up to several hours to apply.


#### Troubleshooting

- "Please grant necessary privilege for live streaming." error means you may need to re-authorize your `name@meltano.com` account to be able to stream to the Meltano YouTube account. You may need to restart your Zoom call for these permissions to take effect.


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


## Community Support Tools

We currently have no SLAs for support but try to respond within 24 business hours across each channel.


### Slack

Slack is our primary way of providing support for the community and most channels redirect folks to Slack to get help.

### Intercom

Intercom is currently embeded on [meltano.com](https://meltano.com). Users can message us here to receive support and are encouraged to join Slack instead of using Intercom. At some point Intercom will be used for lead gen instead.

### ZenDesk

ZenDesk mostly gets transactional emails and job applicants.

- Job applicants get assigned to Douwe Maan if there's no job in Greenhouse, but we should redirect folks to Greenhouse as much as possible.
- Transactional emails get deleted or marked as solved.
  - Emails about WordPress plugin updates get marked as "Solved" so that we have a paper trail of changes if something breaks on the blog.
  - Emails about changes to domains get marked as "Solved" so that we have an audit trail.
  - Emails from Netlify about our available minutes running out get deleted because Netlify will automatically add more minutes if we run out.
- Marketing emails/newsletters are deleted on a case by case basis or assigned to Emily Kyle.


## Community Management Tools

We're piloting a few things and these tools are subject to change.

### Orbit

We're trialing [Orbit](https://app.orbit.love/signup) as a community CRM and activity tracker. Anyone with a `meltano.com` email address can sign up and be granted access to our [workspace](https://app.orbit.love/meltano-e5b745).

### Dots

We're trialing [Dots](https://app.dots.community/) as another community CRM tool. Currently only Amanda Folson has access to this.


## Champions

There are several champions within the community that have been recognized for their contributions and support. These folks are tagged in Orbit with "champion" for now.
