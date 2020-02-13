---
sidebarDepth: 2
---

# Marketing Handbook

## Weekly Content Marketing Activities
Each week, the Meltano team creates a fairly predictable set of content that can be utilized to generate amazing content for marketing purposes.

These items include:

- Kickoff: YouTube video each Monday covering what will be worked on during the week
- Release: the actual software release, which generates a changelog, version number, and all of the previous content for the week
- Demo Day: YouTube video each Friday showing off what has shipped, demonstrated by each authoring participant as available

Each item (linked below) has a corresponding guide to promoting that activity. Each week should roughly follow the following content schedule:

| Day | Content |
| ------ | ------ |
| Monday | [Kickoff blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Content%20Marketing/evergreen-activities.md#promoting-kickoff), [Monday release blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Releases/Promotion%20Guidelines.md) |
| Tuesday | Social promotion of weekly activity | 
| Wednesday | Social promotion of weekly activity | 
| Thursday | [Thursday release blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Releases/Promotion%20Guidelines.md), weekly newsletter | 
| Friday | [Demo day blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Content%20Marketing/evergreen-activities.md#promoting-demo-day) | 


## Email

Meltano uses [Substack](https://meltano.substack.com/) to collect newsletter subscribers and send emails to communicate with our community. Email is opt-in, meaning that by default users can download and install Meltano without providing us any contact information.

## YouTube

Meltano posts numerous videos to YouTube each week, covering everything from product releases to engineering discussions. Meltano videos posted to YouTube should follow a standard template when naming a video and adding a video description. Common naming conventions make it simple to find the latest version of our weekly videos, and an expanded description with information about Meltano and how to contact the team make it easy for individuals who discover a video to get up to speed quickly.

### Naming a YouTube Video

Videos uploaded to YouTube should have names that try and follow the same format wherever possible.

- They always start with “Meltano"
- They then describe the type of recording (Weekly Kickoff, Meeting, Speedrun, Release, Discussion, etc)
- If there’s a specific version of Meltano being referenced, (in a speedrun or release), reference it with a lower-case v followed by the release number (`v1.3.0`)
- Finish with the date in YYYY-MM-DD (`2019-11-01`)
- Separate all names with dashes

Examples of great YouTube video names include:

- Meltano Weekly Kickoff - 2019-10-31
- Meltano Release - v1.3.0 - 2019-10-31
- Meltano Meeting - Marketing Planning - 2019-10-31
- Meltano Discussion - Singer Tap Brainstorming - 2019-10-31

### Writing a YouTube Video Description

Video descriptions should have a short (can be one sentence or phrase) blurb at the beginning, followed by evergreen information about Meltano that can simply be copied and pasted.

Things to consider when writing a great, short, video description:
- Descriptions are short and to the point, explaining what the video is covering and optionally the teams participating (engineering, marketing, leadership, security, etc)
- Don’t worry about “how” something is being worked on, discussed, solved - that’s what the video is for! Description should cover “what, who, why"
- Great descriptions highlight key words/phrases, especially when discussing specific integrations (“we’re discussing how to fix a bug with our Google Analytics data tap”) or an external component (“our data source for XYZ has a new feature”)

Examples of a great YouTube video description include:

```md
Meltano v1.3.0 is publicly released, adding the ability to distill rocket fuel and manufacture widgets, with numerous bug fixes and improvements, including:
- bug fix #1
- improvement #1
- improvement #2
```

```md
The Meltano Engineering team discusses the importance of tabs vs spaces in minified CSS comments when optimizing for compiled code readability.
```

This full example of a Meltano YouTube video description includes evergreen content that should always be included:

```md
Meltano v1.3.0 is publicly released, adding the ability to distill rocket fuel and manufacture widgets, with numerous bug fixes and improvements, including:
- bug fix #1
- improvement #1
- improvement #2

--

Meltano is a free alternative to expensive SaaS tools, providing an integrated workflow for modeling, extracting, loading, transforming, analyzing, notebooking, and orchestrating your data. Meltano integrates the tools you use every day into a single data pipeline, including data from any CSV, Google Analytics, GitLab, Salesforce, Postgres, and much more.

Sign up for our free newsletter: https://meltano.substack.com/

GET STARTED WITH MELTANO
Project Home: https://meltano.com
GitLab: https://gitlab.com/meltano/meltano
Install Meltano: https://meltano.com/developer-tools/self-hosted-installation.html
Tutorials: https://meltano.com/tutorials/

SUBSCRIBE for more videos: http://www.youtube.com/subscription_center?add_user=meltano

Join Us On Slack: https://join.slack.com/t/meltano/shared_invite/enQtNTM2NjEzNDY2MDgyLTZhY2QzYzkwNjYzNWY5Zjk5ZTE1ZGExNzE1NTFmMWJiM2E2ODVhMDFlYjc5YzVjMjllZTZlZDVjNWU2ZjNjNzQ
Blog: https://meltano.com/blog/
GitLab: https://gitlab.com/meltano/meltano
Twitter: https://twitter.com/meltanodata
Newsletter: https://meltano.substack.com/

Meltano
http://youtube.com/Meltano
```

## Distribution Channels

### DigitalOcean Marketplace

Meltano is available as a 1-Click App in the DigitalOcean Marketplace. This allows users to skip the installation and hosting steps, configure a Droplet and immediately begin using the Meltano UI in 60 seconds or less.

#### Linking to our DigitalOcean Marketplace Listing

It is important to form links to our listing in the following way:

`https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322`

This link contains the "deploy" command which allows existing DigitalOcean users to skip the marketplace listing page and go straight to deploying their Droplet. It also includes our referral code, which gets all new DigitalOcean users $50 of free credit over 30 days through the [referral program](https://www.digitalocean.com/referral-program/). We also receive $25 of credit for each new user who spends over $25, which offsets our DigitalOcean bill each month and helps us keep our operating costs low.

Users will find this link on the [Meltano Installation Docs page](/developer-tools/self-hosted-installation.html#digitalocean-marketplace)

#### Following the DigitalOcecan Brand Guidelines

It is important that we be a good partner, creating a win-win for each of us. Please refer to the [DigitalOcean Marketplace Vendor Guide](https://marketplace.digitalocean.com/vendors/getting-started-as-a-digitalocean-marketplace-vendor) for instructions on proper use of logos, language, etc.

## Automation

### Requested Accounts

Meltano provides free hosted accounts to anyone who requests one by filling out a Typeform asking questions about their use case and details needed for setup. After the user provides this information, the form is completed, and a set of automation steps are kicked off via Zapier:

- Zapier receives a notification in realtime that the Typeform has been completed
- Zapier immediately creates a new issue in `meltano/account-management` (private) with the details of the request via the `Typeform Signup to GitLab Issue` Zap. The issue is auto-assigned to the EM and labeled appropriately according to the issue template in the repo.
- Zapier immediately creates a new Contact in ActiveCampaign with the user's name and email address, and adds the Contact to the `Meltano Hosted Applicants` list via the `Typeform Signup to ActiveCampaign Workflow` Zap
- ActiveCampaign immediately sends an email via the `Hosted Applicant Email` automation to the user with instructions on how to schedule a setup call so a walkthrough can occur. This email is sent from `hello@meltano.com` which, when replied to, forwards to the team's support inbox.