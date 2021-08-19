---
sidebarDepth: 2
---

# Engineering Handbook

## Issue tracker best practices

### Milestones

Every open issue should have a [milestone](https://gitlab.com/groups/meltano/-/milestones).
If something we want to happen eventually is not a priority yet, use `Backlog`.
If there is an issue we want to start prioritizing, there is a `Staging` milestone which can be used to alert the Product Lead that this is something we'd like to move into an upcoming milestone. 
If we don't want it to happen, close the issue.

Once an issue becomes a priority, set a sprint milestone (identified by the Friday of the week in question),
even if it's still weeks away and may end up being moved.

New sprint milestones are created about 6 weeks in advance as part of preparation for the weekly kickoff meeting.

#### End of Week Expectations

By the end of day Friday, or the last day of their work week, engineers are expected to:

1. Update the flow label to reflect an accurate status.
2. Close any completed items.
3. Add a progress comment to issues which have the `flow:Doing` label.
4. Issues with the `flow:Review` label will be expected to be closed out once review completes.
   - No need to add a progress comment since action items should be self-documenting.
   - If review is not progressing due to other factors, a `flow:Blocked` label may be appropriate.

This is in preparation for the Product milestone review and [Weekly Kickoff](handbook/product/#weekly-kickoff) on Monday.

### Labels

#### Flow Labels

Every open issue _with a sprint milestone_ should have a `flow` label:

- `flow::Triage` : We are considering removing this label.
- `flow::To Do`: The issue is refined, assigned, and ready to be worked on
- `flow::Doing`: Currently being worked on
- `flow::Blocked`: Blocked by some other issue
- `flow::Review`: Currently in review

These labels do not indicate urgency and should only be used to indicate the work status.

#### Urgency Labels

We have 5 urgency labels:

- `urgency::low`
- `urgency::default`
- `urgency::high`
- `urgency::higher`
- `urgency::highest`

The majority of issues should have the `urgency::default` label, which is a sign that we are accomplishing [the important as well as the urgent](https://www.mindtools.com/pages/article/newHTE_91.htm). 
The `urgency::low` tag can optionally be used to indicate issues that should be the first to be deprioritized.

Issues with the `urgency::default` label, or no urgency label at all, in a milestone have a ~80% chance of being completed within a milestone. 
Issues with the `urgency::low` label have a ~50% chance of being completed within a milestone. 
We aim to close 100% of issues with `urgency::high` or above within the milestone.

The `urgency::highest` should be resolved for urgent user-facing issues such as the website going down - and should be resolved within 24 hours or less.
If an issue of this type is moved to another milestone because it was not completed, the urgency should most likely be increased.

If there is an issue of particular interest, add the `urgency::high` label to it and leave a comment tagging Taylor with a note explaining why you believe it's a high urgency.

#### Kind Labels

All issues should have a label indicating its kind:

- `kind::Bug`
- `kind::Feature`
- `kind::Tech Debt`
- `kind::Risk` 

These kinds map onto the [Flow Framework](https://flowframework.org/) items of Feature, Defect, Debt, and Risk. 
These are meant to be mutually exclusive and collectively exhaustive, meaning an issue will have 1 and only 1 of these labels. 
There is a fifth label available for filtering purposes: `kind::Non-Product` which is used for administrative and business-related issues.

| Kind Item      | Delivers                                  | Description                                                           | Example Artifacts                                    |
|----------------|-------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------|
| Features       | New business value                        | New value added to drive a business result; visible to the customer   | Epic, user story, requirement                        |
| Bugs (Defects) | Quality                                   | Fixes for quality problems that affect customer experience            | Bug, problem, incident, change                       |
| Risks          | Security, governance, compliance          | Work to address security, privacy, and compliance exposures           | Vulnerability, regulatory requirement                |
| Tech Debts     | Removal of impediments to future delivery | Improvement of the software architecture and operational architecture | API addition, refactoring, infrastructure automation |

*This table is sourced from "Project to Product" by Mik Kersten.*

FAQ:

* Q: Where would documentation issues fit? 
  * A: Documentation issues will most likely be considered a Bug if they are not delivered as part of a Feature.

It is the responsibility of the Product team to add this label, but Engineers are welcome to add it as well.

#### Value Stream Labels

All issues should have a label indicating its value stream:

- `valuestream::Meltano`
- `valuestream::Hub`
- `valuestream::SDK`
- `valuestream::Academy`
- `valuestream::Ecosystem` - This is a bit of a catchall for general "community" type work that benefits the Meltano and Singer communities but does not neatly fit into another value stream. 

These map to our "product lines" and are used to understand allocation of work across the value streams.
There is an additional label for filtering purposes: `valuestream::BusinessOperation` which is used for administrative and business-related issues.

These value streams are inspired by the [Flow Framework](https://flowframework.org/) and are useful for understanding every bit of work that goes into the products that deliver value for users and, eventually, customers.

It is the responsibility of the Product team to add this label, but Engineers are welcome to add it as well.


#### Meltano Area Labels

If appropriate, an issue should have a stage label (one of the letters in "meltano"):
- `Model`
- `Extract`
- `Load`
- `Transform`
- `Analyze`
- `Notebook` (currently unused)
- `Orchestrate`

The value of these labels is under discussion as forcing them to fit the Meltano acronym may not be optimal. 
We want a way to indicate the part of Meltano specifically that the work applies to, such as transformation, integration, etc.

#### Other Labels

- `Discussion` for issues that require more discussion
- `Exploration`
- `Community Support`
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

## Merge Request (MR) Process

### Trivial Updates

All non-trivial merge requests should be reviewed and merged by someone other than the author.
A merge request that touches code is never trivial, but one that fixes a typo in the documentation probably is.

Trivial updates, such as docs updates, do not require a logged issue.

### MR Review Process

All team members are encouraged to review community contributions. However, 
each MR should have a single accountable reviewer, who is also approved as a CODEOWNER. That 
reviewer can ask others in the team for feedback but they are solely accountable for the merge/approval
decision.

If you are assigned as primary reviewer and _do not_ feel confident in your ability to approve and merge,
it is your responsibility to either (a) request assist from a team member on specific parts of the code,
or (b) ask another team member to take the role of primary reviewer.

### Approval Stickiness

MR approvals are set (on a per-repo basis) to _not_ use the option to `Remove all approvals when commits are added to source branch`. This means approvals are "sticky" and can be requested any time during the review cycle. This also means it is the Merger's responsibility to check commit history and raise an alarm on any regressions or other concerns introduced _after_ another team member granted their approval.

**Security Note:** In most cases, the closing "post-approval" tasks should be cosmetic - such as docs, linting, and changelog updates - but team members should nevertheless be on the lookout for any regressions or malicious-looking code that may have been added _after_ approvals are given and _before_ the Merge is applied. (If in doubt, please request a repeat-review from other approvers on the MR.)

### Team-Authored MRs

Team authored MRs may be reviewed by any other team member, but should also be approved by a Manager (probably AJ), as described below.

### Community-Contributed MRs

For community contributions, the community contributor should indicate readiness to merge and
the core team member (primary reviewer) will approve the MR and also perform the merge.

All Community-Contributed MRs should have their corresponding Issue marked with the `Community-Contributed MR` label in Gitlab. This helps in prioritization of code contributions. We aim to be responsive in all Community-Contributed MRs, as a sign of respect for the community members' contributed time and effort.

The first team member to review should assign themselves to the review and check the following are present:

- Soundness of code changes (the "meat" of the review)
- Description of manual testing performed (where applicable)
- Presence of unit testing for new capabilities, where applicable
- Presence of docs and changelog updates, where applicable

**Note:** If not comfortable being primary approver, due to either time constraints or subject matter expertise, the first reviewer should request review by tagging another team member.

#### Guiding Principles for Community Contributions

- We prioritize code contributions as high-value work, honoring the generous and valuable donation of a contributor's time and effort. We honor those contributions as representing the authors' valuable time and energy, and we respond to them in a time-sensitive manner.
- Whenever blocked on a response for 24+ hours, we flag as such using the `Waiting on Contributor` label. Sparingly and with due respect, we may ping a contributor on Slack (in DM or in the `#contributing` channel) to notify them of pending action on their side.
- In the case that a contributor becomes non-responsive due to competing priorities, time lag, or other factors, we evaluate internally within the team (and with help from Product) to decide if we can prioritize and deliver any remaining outstanding tasks ourselves.

### Manager-Level Approval

For both Community-Contributed MRs and Team-Authored MRs, a Manager-Level approval is required for any non-trivial updates - in addition to Team Member approval. This can be requested either when the MR foundation is in place or as a "final check". The manager-level approval should generally be requested _after_ the MR is otherwise "clean" - and after known action items and questions are called out in the text of the MR.

The goal in the dual-approval approach is to create a virtuous cycle of individual ownership combined with manager-level accountability, while fostering organic and supportive training opportunities for new team members.

- **Note:** In future, as we scale, we will replace "Manager-Level" approval with "Senior-Level" approval or similar.

### Responsibility to Merge

- Core team members may merge their own MRs once necessary approval(s) are provided.
- When nearing completion, an MR author may also invite the reviewer
to "merge if approved", in order to reduce cycles spent in back-and-forth.
- Except in exceptional circumstances, a reviewer should not merge
the MR on behalf of the other team member unless invited to do so.

### Continually improving Contribution Guidelines

As experts catch issues in MRs that the original reviewers did not,
we will update this section and the [Contributor Guide](/docs/contributor-guide.md#reviews),
and reviewers will learn new things to look out for until they catch (almost) everything the expert would,
at which points they will be experts themselves.

## Useful issue boards

- [Development Flow](https://gitlab.com/groups/meltano/-/boards/536761), with a column for each `flow::` label. Don't forget to filter by milestone, and/or assignee!
- [Kind](https://gitlab.com/groups/meltano/-/boards/2917606) - useful for understanding the distribution of work across the different flow types (Bug, Feature, etc.)
- [Value Stream](https://gitlab.com/groups/meltano/-/boards/2917637) - useful for understanding the distribution of work acrss the different product areas of Meltano
- [Urgency](https://gitlab.com/groups/meltano/-/boards/2917749) - useful for understanding the overall priority of issues in a milestone.
- [Milestone](https://gitlab.com/groups/meltano/-/boards/1933232) - used to move issues easily between milestones.
- [Office Hours](https://gitlab.com/groups/meltano/-/boards/2923184) - used to tee up issues for community discussion and review, generally directly
before and/or after implementing an important user-facing feature.

## Release Process

The process below applies to both Meltano and then SDK, unless otherwise noted.

### Evergreen Release Process

We are always releasing, and we aim to have an _evergreen_ release process, handling the operational release and marketing work simultaneously while performing development.

### The Release Checklist

All release steps are documented in the Gitlab issue template, and a new `Release` checklist issue should be created each time one is closed. 

In either the SDK or Meltano project on Gitlab, begin a new issue and select the `Release` template from the dropdown options.

### Schedule

The release schedule is determined by Product and Marketing. The Engineering team aims to _always_ be ready to ship, with sufficient automation and documentation in place to allow _anyone_ in the company to perform the role of Release Manager.

### Rotating Release Managers

We have a sliding window of `Release Manager` role within the Engineering team, with the prior `Release Manager` oncall to support the next `Release Manager`. If issues arise or a second opinion is needed during release, the last person who ran the release process will perform this supporting function for the next.

### Versioning

Regular releases get a minor version bump (`1.1.0` -> `1.2.0`).
Releases that only address regressions introduced in the most recent release get a patch version bump (`1.2.0` -> `1.2.1`).

### Version Bump Processes

The Meltano and the SDK version bump processes are documented in the Release issue templates. No further actions are needed besides what is listed in the checklist.

## Zoom

For community calls, use one of the following background in Zoom depending on whether you mirror your video or not.

Note that if you mirror your video then the image will look backwards on your screen, but to others in the call it will look correct.

![Meltano Background](/images/zoom-backgrounds/meltano-background.png)

Add it by doing the following:

* Download the file and store it on your computer
* Navigate to Preferences
* Click Background & Filters
* Within Virtual Backgrounds, click the `+` icon and add the file

## Outages & escalation

Both https://www.meltano.com and https://meltano.meltanodata.com are automatically monitored using Pingdom, with notifications of downtime posted to:
- Zendesk, through our `hello@` email address, and
- Douwe, by email and SMS.

Other `*.meltanodata.com` instances are not currently monitored.

When any instance managed by us is reported to be down, through Pingdom or any other means, resolving this becomes the team's top priority.

## GitHub Mirrors

We mirror the three main Meltano repositories (meltano/sdk/hub) from GitLab to GitHub. This is managed via the "Mirroring repositories" section with the Settings of the GitLab repository. The push was created using Taylor's personal GitHub account (tayloramurphy) with a personal access token made just for the use case. This was tracked in [this issue](https://gitlab.com/meltano/meta/-/issues/55).

## Domain names, DNS, and hosting

Domain names are typically registered with [Amazon Web Services](/handbook/tech-stack/#amazon-web-services).
[NameCheap](/handbook/tech-stack/#namecheap) can be used if a TLD is not available there.
For legacy reasons, one domain name is still registered with [Gandi](/handbook/tech-stack/#gandi).

DNS is typically managed at [SiteGround](/handbook/tech-stack/#siteground).
DNS for `*.meltanodata.com` is managed at [DigitalOcean](/handbook/tech-stack/#digitalocean).
DNS for `singerhub.io` is managed at [NameCheap](/handbook/tech-stack/#namecheap).

<https://meltano.com> is hosted at [SiteGround](/handbook/tech-stack/#siteground).
<https://hub.meltano.com> is hosted using [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/) for <https://gitlab.com/meltano/hub>.
<https://sdk.meltano.com> is hosted at [Read the Docs](/handbook/tech-stack/#read-the-docs).

## SQL Style Guide

Our SQL style guide is located [at this link](/handbook/engineering/sql-style-guide.html). It is heavily inspired by the [GitLab SQL Style Guide](https://about.gitlab.com/handbook/business-technology/data-team/platform/sql-style-guide/).
