---
sidebarDepth: 2
---

# Product Handbook

Our [milestones and scheduled work](https://gitlab.com/groups/meltano/-/milestones) is available to the public, and we encourage anyone to [submit new issues](https://gitlab.com/meltano/meltano/issues/new).

## High-level Responsibilities

The Head of Product will review any [new issues](https://gitlab.com/groups/meltano/-/issues) in the Meltano group on a daily cadence and organize appropriately with labels and milestones.

## Choosing What to Work On

We have limited engineering hours and focus available, and need to make sure we are working on things that will move Meltano forward towards our goal of increasing [MAUI](https://meltano.com/docs/roadmap.html#maui).

When evaluating a new major piece of work, we create an exploratory issue and use an opportunity assessment (some people call this "Market Requirement Doc" or MRD) to ask the following questions:

1. Exactly what problem will this solve? (value proposition)
2. For whom do we solve that problem? (target market)
3. How big is the opportunity? (market size)
4. What alternatives are out there? (competitive landscape)
5. Why are we best suited to pursue this? (our differentiator)
6. Why now? (market window)
7. How will we get this product to market? (go-to-market strategy)
8. How will we measure success/make money from this product? (metrics/revenue strategy)
9. What factors are critical to success? (solution requirements)
10. Given the above, what’s the recommendation? (go or no-go)

The [opportunity assessment was created by Marty Cagan at Silicon Valley Product Group](https://svpg.com/assessing-product-opportunities/)

## Product Cadence

We ship a new release every Monday, and always have a backlog of opportunity assessments to write and explore. However, given the stage of Meltano (pre-product/market fit) we don't plan specific work items more than a few weeks in the future.

## MR First

If you want to make an improvement to Meltano you don't have to wait for Product approval, kick-off some long convoluted dicsussion, or worry about stepping on anyone's toes. Submit a Merge Request (MR) with your proposed changes and we can iterate from there.

## "AND not OR" Mentality

As an internal startup we are constrained by our team size and the hours in the day, so we have to make smart trade-offs about the order and prioritization of what we do. Our goal is to chose the things that will unlock MAUI growth.

Sometimes, it can feel like we are chosing between two important things and this can be painful. However, we take the approach that anything is technically possible to build on the Meltano team so it's a just a question of the order of operations. On a long enough timeline, we will do everything we put on the roadmap -- so keep writing issues and hold onto that "it's an AND, not OR" mindset.

## Weekly Kickoff

Every Monday we have a Kickoff call to highlight for the community what the priorities are for the week. Prior to the actual call, there are several work items to do.

### Friday - Last day of Milestone

* Create a kickoff issue highlighting the general priority for the next week.
  * Title: `Weekly Kickoff for Milestone - <milestone>`
  * Due Date for the Monday of the milestone

### Monday - Kickoff Day

Before the Kickoff Call:

* Review and roll community issues to the next milestone
* Roll merge requests
* Everyone on the team should roll their own issues to the next milestone. Take the time to review the current status of issues and align priorities with the kickoff issue.

Kickoff Call:
* Check-in with everyone
* Highlights & lowlights from previous week
* Confirm general priorities and do a soft review of boards
* Review Metrics
* Start livestream
  * Talk about general priority
  * Walk through issues

After the Kickoff Call:
* Close the previous milestone
* Close Kickoff issue

## Open Source Projects We're Keeping an Eye On

This section is dedicated to tracking interesting open source projects that we want to keep an eye on that we don't already have plans to integrate with.
This [article from BVP](https://www.bvp.com/atlas/roadmap-data-infrastructure/) is useful as well.

* [Evidence](https://www.evidence.dev/)
* [Lightdash](https://www.lightdash.com/) - BI, integrates with dbt
* [metriql](https://metriql.com/) - Headless BI
* [Rudderstack](https://rudderstack.com/) - Customer Data Platform
* [Soda SQL](https://github.com/sodadata/soda-sql) - Data Testing and Monitoring

Additionally, there are many "git for data" tools tracked in [this spreadsheet](https://docs.google.com/spreadsheets/d/1jGQY_wjj7dYVne6toyzmU7Ni0tfm-fUEmdh7Nw_ZH0k/edit#gid=0).
[Project Nessie](https://projectnessie.org/) is another option not listed in the sheet.
