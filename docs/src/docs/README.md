---
description: Learn where to use Meltano, how Meltano is built, and where to get started.

members:
- name: Douwe Maan
  title: Founder & CEO
  location: Mexico City, Mexico 🇲🇽
  gravatar_hash: 73d1548ae618321220679b3a4fda7fb1 # md5(email)
  social:
    gitlab: DouweM
    twitter: DouweM
    linkedin: douwem
- name: Taylor Murphy
  title: Head of Product & Data
  location: Arlington, TX, USA 🇺🇸
  gravatar_hash: b4936f876b1093f90d7246b264084ddd
  social:
    gitlab: tayloramurphy
    twitter: tayloramurphy
    linkedin: tayloramurphy
- name: AJ Steers
  title: Head of Engineering
  location: Seattle, WA, USA 🇺🇸
  gravatar_hash: 80b61ad103a8d9fd989893b757b15dac
  social:
    gitlab: aaronsteers
    twitter: aaronsteers
    linkedin: aaronsteers
- name: Emily Kyle
  title: Director of Marketing
  location: Austin, TX, USA 🇺🇸
  gravatar_hash: ad3bd918d010568b6ce9c5a6a08f0086
  social:
    gitlab: Emily
    twitter: emilylucie
    linkedin: emilylucie
- name: Amanda Folson
  title: Developer Relations Manager
  location: Land o' Lakes, FL, USA 🇺🇸
  gravatar_hash: fe416b883fb81a12313becdf9a29692c
  social:
    gitlab: afolson
    twitter: AmbassadorAwsum
    linkedin: violins
- name: Edgar Ramírez Mondragón
  title: Senior Backend Engineer
  location: Mexico City, Mexico 🇲🇽
  gravatar_hash: a89b7e5a5d6ea347878ea4042ae31dff
  social:
    gitlab: edgarrmondragon
    twitter: cofonlafaefe
    linkedin: edgarrmondragon
- name: Florian Hines
  title: Staff Backend Engineer
  location: San Antonio, TX, USA 🇺🇸
  gravatar_hash: 88529f59d3f298bcc9e2a705dc1f1c68
  social:
    gitlab: pandemicsyn
    twitter: pandemicsyn
    linkedin: florianhines
- name: Ken Payne
  title: Backend Engineer
  location: London, UK 🇬🇧
  gravatar_hash: 778b432070eba884662a752b184dac7b
  social:
    gitlab: kgpayne
    linkedin: k-g-payne
- name: Pat Nadolny
  title: Senior Data Engineer
  location: Brooklyn, NY, USA 🇺🇸
  gravatar_hash: aa4b6175db043b7bfe3177cdc18318c9
  social:
    gitlab: pnadolny13
    linkedin: patnadolny
- name: S. P.
  title: Operations Analyst
  location: CA, USA 🇺🇸
openings:
- title: Head of Partnerships
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4088646004
- title: Technical Marketing Manager
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4075560004
- title: Content Marketing Manager
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4144713004
- title: DataOps Evangelist
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148045004
- title: Senior Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4117149004
- title: Senior Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4117149004
- title: Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148049004
- title: Backend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4148049004
- title: Senior Frontend Engineer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4067842004
- title: Senior UI/UX Designer
  location: Anywhere, Remote 🌍
  description_url: https://boards.greenhouse.io/meltano/jobs/4147449004
---

# Introduction

[Meltano](https://meltano.com) is ELT for the DataOps era:
[open source](https://gitlab.com/meltano/meltano),
[self-hosted](/docs/production.html),
[CLI-first](/docs/command-line-interface.html),
[debuggable](/docs/command-line-interface.html#debugging), and
[extensible](/docs/plugins.html).

This page covers the project's [Mission](#mission), [Focus](#focus), [Roadmap](#roadmap), [History](#history), and [Team](#team).

To find guides and references on other topics, use the Table of Contents in the sidebar.

## Mission

Our mission is to enable everyone to realize the full potential of their data.

Our vision is for Meltano to become the foundation of every team's ideal data stack.

Our CEO, Douwe Maan, wrote a detailed post about why we believe in this mission and vision [here](https://meltano.com/blog/meltano-the-strategic-foundation-of-the-ideal-data-stack/).


## Contributing

Meltano is built for and by its community, and we welcome your contributions to our [GitLab repository](https://gitlab.com/meltano/meltano),
which houses Meltano's
[core](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/core),
[CLI](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/cli),
[UI](https://gitlab.com/meltano/meltano/-/tree/master/src/webapp),
[UI API](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/api),
[these docs](https://gitlab.com/meltano/meltano/-/tree/master/docs/src), and
the [index of discoverable plugins](/docs/contributor-guide.html#discoverable-plugins),
which feeds the lists of [Extractors](https://hub.meltano.com/extractors/) and [Loaders](https://hub.meltano.com/loaders/) that are supported out of the box.

To learn more about contributing to Meltano, refer to the [Contributor Guide](/docs/contributor-guide.html).

## History

Meltano was [founded](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/) inside [GitLab](https://about.gitlab.com/) in 2018 to serve the GitLab Data Team. Meltano started as an open source tool built for GitLab’s data and analytics team, who wanted an end-to-end data platform built around open source components and DevOps principles. You can read more about our history via our [handbook](https://handbook.meltano.com/timeline).

## Team

Meltano is built by an all-remote team of {{$frontmatter.members.length}} and a [community](/docs/community.html) of [contributors](/docs/contributor-guide.html).
If you'd like to join the team, check out the [career opportunities](#careers) below!

<TeamGrid :members="$frontmatter.members" />

## Careers <a name="job-openings" />

The team is growing: we're planning to bring on {{$frontmatter.openings.length}} more people in the near future! 

If our [mission](#mission) excites you, and you think could make a difference, we'd love to talk to you. Apply directly through the [job openings](https://boards.greenhouse.io/meltano) below!

<TeamGrid :openings="$frontmatter.openings" />

### Employee Perks
* Unlimited PTO
* Professional Development Support and Budget
* Remote Working
* Reimbursable coworking fees and external office space
* Budget for Office equipment and workspace supplies
* Team Offsites
* Access to world class founders, investors and mentors
