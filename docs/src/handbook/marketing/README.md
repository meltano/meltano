---
sidebarDepth: 2
---

# Marketing Handbook

## Weekly Community Activities
The Meltano convenes regularly to generate content for community and learning purposes.

These items include:

- **Weekly Kickoff**: Livestream each Monday covering what will be worked on during the week
- **Office Hours**: Community meeting for discussion about upcoming features and general Q&A
- **Demo Day**: Community meeting every other Thursday showing off what has shipped, demonstrated by each authoring participant as available
- **Meltano / SDK Release**: the actual software release, which generates a changelog, version number, and all of the previous content for the week

Each item (linked below) has a corresponding guide to promoting that activity. Each week should roughly follow the following content schedule:

| Day | Content |
| ------ | ------ |
| Monday | [Kickoff blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Content%20Marketing/evergreen-activities.md#promoting-kickoff), [Monday release blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Releases/Promotion%20Guidelines.md) |
| Tuesday | Social promotion of weekly activity |
| Wednesday | Social promotion of weekly activity |
| Thursday | [Thursday release blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Releases/Promotion%20Guidelines.md), weekly newsletter |
| Friday | [Demo day blog & promotion](https://gitlab.com/meltano/meltano-marketing/blob/master/Content%20Marketing/evergreen-activities.md#promoting-demo-day) |


## Meltano Brand Kit

### Brand Personality
Our personality is built around four main characteristics.

* **Human**: We write like we talk. We avoid buzzwords and jargon, and instead communicate simply, clearly, and honestly.
* **Competent**: We aim to be masterly at what we offer, and communicate with conviction.
* **Humble**: We care about helping those around us achieve great things more than we care about our personal accomplishments.
* **Inclusive**: We embrace new ideas, new voices and new perspectives. We are always happy to be educated.
* **Fun**: We like Shramp and other oddities. 

### Tone of Voice
Friendly, informative yet ambitious. We bring empathy to all interactions and stewardship to those new to the space. 

### Brand Resources
Coming Soon! (Fonts, Colors, Logos, Slide decks and much more)


### Talking about the Meltano Product Family and Team

As of 2021 we have 3 main "product lines". Each of these should be referenced in speech and text communications in specific ways.

### Meltano

#### Product/Project
  
**Recommended**

    * Meltano
    * The Meltano Open-Source Project

     Example usage: Last week, a new version for Meltano was released

**Incorrect**

    * The Meltano

    Example usage: Last week, a new version for the Meltano was released

### SDK

Note that Targets can be substituted for Taps in each of these examples

**Recommended**

    * The Meltano SDK
    * The Meltano Tap SDK
    * The Meltano SDK for Taps
    * The Meltano SDK for Singer Taps

    Example usage: Today we're releasing a new update for the Meltano Tap SDK that...

**OK**

    * The SDK
    * The Tap SDK
    * The SDK for Taps
    * The SDK for Singer Taps
    * Meltano's Tap SDK
    * The Tap SDK by Meltano

    These are OK when the proper, Meltano-specific name has already been referenced. 
    Example usage: Today we're releasing a new update for the SDK for Taps that...

**Incorrect**

    * Singer SDK
    * Singer SDK for Taps
    * singer-sdk
    * Singer's SDK
    * Meltano's Singer SDK
    * Singer SDK by Meltano

    Incorrect example usage: Today we're releasing a new update for the Singer SDK for Taps that...

### MeltanoHub

**Recommended**

    * MeltanoHub
    * MeltanoHub for Singer
    * The Hub

    Example usage: Today we're releasing an update for MeltanoHub for Singer to...

**Incorrect**

    * The MeltanoHub
    * The SingerHub
    * The Hub for Singer

    Incorrect example usage: Today we're releasing an update for the MeltanoHub for Singer to...

#### Team

**Recommended**

    * the Meltano Team
    * the Meltano Core Team

    Example usage: The Meltano Team is announcing today...

**Incorrect**

    * The Meltano

    Incorrect example usage: The Meltano is announcing today...

## Meltano Newsletter

Meltano uses [Substack](https://meltano.substack.com/) to collect newsletter subscribers and send emails to communicate with our community. Email is opt-in, meaning that by default users can download and install Meltano without providing us any contact information.

## Meltano Blog

Want to hear everything we are talking and thinking about internally and in the open source data would. Follow along, it's easy!

### Naming a Blog Post
Start with the title of the post, be as descriptive as possible but succinct. Do not begin with the date. Only include a date if the content will not be evergreen and it is critical to note the date for the timeliness of the post. Adding a date to the title will instantly date the post and generally when people are looking for content they are not looking for when it was published more what they can learn in the post. 

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
- Timestamps can be linked to just by writing the timestamp: `1:33`.

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
- bug fix #1 (link)
- improvement #1 (link)
- improvement #2 (link)

1:55​ Meltano team - who we are...
3:15​ Discussion of bug fix #1

## Social

## Social Channels

| Channels |
| ------------------------------------------ |
| [Meltano Twitter](https://twitter.com/meltanodata) |
| [Meltano LinkedIn](https://www.linkedin.com/company/meltano/) |
| [Meltano Facebook](https://www.facebook.com/meltano) |
| [Meltano Instagram](https://www.instagram.com/meltanodata/) |
| [Meltano YouTube](https://www.youtube.com/meltano) |

### Channel Use

#### Twitter <a name="twitter"></a>
* **What do we use it for?**
  * New, engagement, announcements, releases/ key feature announcements, company announcements, info gathering (polls)

#### LinkedIn <a name="linkedin"></a>
* **What do we use it for?**
  * Hiring, thought leadership, sharing media
* **relevant topics?**
  * trends, best practices, events, jobs, key features, investments, partners, culture topics, remote work stuff
* other considerations 
* **What content performs well**
  * photos and text, suggest using tags (to expand reach) and hashtags, around 3 is optimal (use keywords you want to be associated with)
  * Provide a call to action

#### Facebook <a name="facebook"></a>
* **What do we use it for?**
  * Hiring, thought leadership, sharing media, events, news, community building
* **relevant topics?**
  * best practices, events, jobs, how tos, investments, partners, culture topics, remote work stuff
* other considerations 
* **What content performs well**
  * photos, vidoes and text
  * Provide a call to action

#### Instagram <a name="instagram"></a>
* coming soon

#### TikTok <a name="tiktok"></a>
* coming soon

#### Slack <a name="slack"></a>
* **What do we use it for?** 
  * Community engagement, announcements, support, releases (consider info gathering)
* **target audience?**
   * core community members, super fans, those getting started, trying to learn 
* **Suggested posting cadence?**
  * TBD- don't change until we update metrics
* **relevant topics?**
  * announcements, new releases, key features, 
* **other considerations**
  * Use it to cross-promote partners and top community members

#### YouTube <a name="youtube"></a>
* **What do we use it for?**
  * long-form content, training, informational/ deep learning
* **target audience?**
  * Anyone looking to learn about how we work, function and the product
* **relevant topics?**
  * thought leadership, product demos and deep dives, road map walkthroughs, office hours, demo days, pitch deck overviews 
* **other considerations** 
  * need to be careful and curate and tag appropriately. 

#### Stack Overflow <a name="stackoverflow"></a>  
* coming soon

#### Hacker news <a name="hackernews"></a>  
* **What do we use it for?**
  * deep community and subject matter engagement
  * Product discussions, thought leadership
* **target audience?**
  * Developers, SREs/ops folks, and some data folks. Overall a pretty technical audience.
  * FOSS advocates
* **Suggested posting cadence?**
  * Post our jobs on the monthly "Who's hiring?" thread as needed.
  * Don't submit our own content to HN. Let our own community members post to HN organically.
* **relevant topics?**
  * We could participate in more data/dataops threads, but right now we only show up when someone is talking about us.
* **other considerations**
  * The HN community values transparency so you should disclose that you're an employee of Meltano when responding to Meltano-related threads.

Internal folks find out more in [this issue](https://gitlab.com/meltano/marketing/marketing-general/-/issues/30)


--

Meltano is ELT for the DataOps era: open source, self-hosted, CLI-first, debuggable, and extensible.

Pipelines are code, ready to be version controlled, containerized, and deployed continuously. Develop and test locally, then deploy in production along with the built-in Airflow integration, or inside your orchestrator of choice.

Meltano embraces the Singer standard and its community-maintained library of open source extractors and loaders, and leverages dbt for transformation.

GET STARTED WITH MELTANO
Project Home: https://meltano.com
GitLab: https://gitlab.com/meltano/meltano
Install Meltano: https://meltano.com/docs/installation.html
Tutorials: https://meltano.com/tutorials/

SUBSCRIBE for more videos: http://www.youtube.com/subscription_center?add_user=meltano

Join Us On Slack: https://join.slack.com/t/meltano/shared_invite/zt-obgpdeba-7yrqKhwyMBfdHDXsZY8G7Q
Blog: https://meltano.com/blog/
GitLab: https://gitlab.com/meltano/meltano
Twitter: https://twitter.com/meltanodata
Newsletter: https://meltano.substack.com/
```
