---
title: Merge Request Process
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 3
---

## Merge Requests

<div class="notification is-info">
  <p><strong>Searching for something to work on?</strong></p>
  <p>Start off by looking at our <a href="https://gitlab.com/groups/meltano/-/issues?scope=all&state=opened&label_name[]=Accepting%20Merge%20Requests">"Accepting Merge Requests"</a> label. Keep in mind that this is only a suggestion: all improvements are welcome.</p>
</div>

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer may approve the merge request or send it back for further iteration
1. Once approved, the merge request can be merged by any Meltano maintainer

### Reviews

A contributor can ask for a review on any merge request, without this merge request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the merge request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a merge request without feedback, unless specified by the reviewer.

## Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ poetry run changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.