---
title: Contributor Guide
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
redirect_from:
  - /the-project/community/
weight: 1
---

Thank you for your interest in contributing! Meltano is built for and by its community, and we welcome your contributions to the project. Read on to find out how to get started.

## Code of Conduct

Before getting started, please make sure you review our Code of Conduct. Everyone interacting in Slack, codebases, issue trackers, mailing lists, events, or other Meltano activities is expected to follow [this code of conduct](https://www.python.org/psf/conduct/). If you are unable to abide by the code of conduct set forth here, we encourage you not to participate in the community. If you see a violation please notify us by messaging `@Amanda Folson` on Slack.

## Ways to Contribute

There are multiple ways to contribute to Meltano:

- [The Meltano Project](https://gitlab.com/meltano/meltano/) - Suggest new features for Meltano, report bugs, or open Merge Requests to fix issues.
- [Meltano SDK](https://sdk.meltano.com/en/latest/) for Taps and Targets
- [Plugins, taps/targets]() or adding taps/targets to [MeltanoHub](https://hub.meltano.com) - If you've made a tap, target, or other plugin, you can add it to the MeltanoHub for others to discover and use.
- [Documentation](https://docs.meltano.com/)
- [Tutorials](https://docs.meltano.com/tutorials/) and [Blog Posts](https://meltano.com/blog)
- Helping on [Slack](https://meltano.com/slack)
- [Company Handbook](https://handbook.meltano.com)

We also invite you to open issues and merge requests on any of our repositories to report bugs, suggest new ideas and features, or fix issues you encounter.

There are also several community events you may be interested in:

- [Office Hours](https://handbook.meltano.com/marketing/community#office-hours)
- [Demo Day](https://handbook.meltano.com/marketing/community#demo-day)
- [Singer Working Group](https://github.com/MeltanoLabs/Singer-Working-Group)

## Where do I start?

If you'd like to contribute, but you're not sure _what_, check out the list of open issues labeled [Accepting Merge Requests](https://gitlab.com/meltano/meltano/-/issues?sort=created_date&state=opened&label_name[]=Accepting+Merge+Requests). Any other improvements are welcome too, of course, so simply asking yourself "What could have been better while I was using Meltano?" is another good way to come up with ideas.

If an issue for your problem or suggested improvement doesn't exist yet on our [issue tracker](https://gitlab.com/meltano/meltano/-/issues),
please [file a new one](https://gitlab.com/meltano/meltano/-/issues/new) before submitting a [merge request](/contribute/merge),
so that the team and community are aware of your plan and can help you figure out the best way to realize it.

<div class="notification is-warning">
  <p><strong>Searching for something to work on?</strong></p>
  <p>Start off by looking at our <a href="https://gitlab.com/groups/meltano/-/issues?scope=all&state=opened&label_name[]=Accepting%20Merge%20Requests">"Accepting Merge Requests"</a> label. Keep in mind that this is only a suggestion: all improvements are welcome.</p>
</div>

## Contribution Guides

The following guides have information to help get you up and running and ready to contribute.

<ul>
  {% assign items = site.contribute | sort: "weight" %}
  {% for doc in items %}
    <li><a href="{{ doc.url }}">{{ doc.title }}</a></li>
  {% endfor %}
</ul>
