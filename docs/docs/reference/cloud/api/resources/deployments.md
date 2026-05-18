---
title: Deployments
description: Matatika Deployments resource reference documentation
permalink: /api/resources/deployments
parent: Resources
grand_parent: API
nav_order: 19
components: request-md-components/deployments
---

# {{page.title}}

Deployments let the user schedule a [job](jobs) to deploy the contents of their [workspace](workspaces) repository to their workspace in the Matatika cloud.
{: .fs-5 }
This can be done manually or via a GitHub Webhook which you can see how to set up in our Quick Start Guide: [Workspace Deploy Hook]({{site.baseurl}}/how-to-guides/manage-workspaces/managing-config-from-github)


---

#### Requests

- TOC
{: toc }

---

{% include {{ page.components }}/deploy-workspace.md %}

{% include {{ page.components }}/github-webhook.md %}