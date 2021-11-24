---
description: Meet the team behind Meltano

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
---

# Team

Meltano is built by an all-remote team of {{$frontmatter.members.length}} and a [community](/docs/community.html) of [contributors](/docs/contributor-guide.html).
If you'd like to join the team, check out our [job openings](/jobs/)!

<TeamGrid :members="$frontmatter.members" />
