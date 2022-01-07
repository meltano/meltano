---
title: Getting Started
description: Learn how to use Meltano for data analysis of CSVs, Postgres, Google Analytics, GitLab, and much more.
layout: doc
weight: 1
---

<div class="notification is-info">
  <p><strong>Contributions are welcome!</strong></p>
  <p>If there's a guide you want to see that's not here, we welcome contributions to add it! Submit a <a href="https://gitlab.com/meltano/meltano/-/tree/master/docs/src/tutorials">merge request</a> with your guide and the Meltano team will help you polish it for release. You may also <a href="https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=">submit an issue</a> to help us gauge interest in new guides.</p>
</div>

<ul>
  {% for gs in site.getting-started %}
    <li><a href="{{ gs.url }}">{{ gs.title }}</a></li>
  {% endfor %}
</ul>