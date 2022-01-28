---
title: The Project
description: Information about the Meltano Project and its community.
layout: doc
hidden: true
toc: false
---

<div class="notification is-info">
  <p><strong>Contributions are welcome!</strong></p>
  <p>If there's a document you want to see that's not here, we welcome contributions to add it! Submit a <a href="https://gitlab.com/meltano/meltano/-/tree/master/docs/">merge request</a> with your doc and the Meltano team will help you polish it for release. You may also <a href="https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=">submit an issue</a> to help us gauge interest in new docs.</p>
</div>

## Index

<ul>
  {% for doc in site.the-project %}
    <li><a href="{{ doc.url }}">{{ doc.title }}</a></li>
  {% endfor %}
</ul>