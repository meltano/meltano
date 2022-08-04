---
title: Meltano Concepts
description: Information about Meltano Concepts.
layout: doc
hidden: true
toc: false
---

<div class="notification is-info">
  <p><strong>Contributions are welcome!</strong></p>
  <p>If there's a document you want to see that's not here, we welcome contributions to add it! Submit a <a href="https://github.com/meltano/meltano/tree/main/docs">pull request</a> with your doc and the Meltano team will help you polish it for release. You may also <a href="https://github.com/meltano/meltano/issues/new">submit an issue</a> to help us gauge interest in new docs.</p>
</div>

## Index

<ul>
  {% for doc in site.concepts %}
    <li><a href="{{ doc.url }}">{{ doc.title }}</a></li>
  {% endfor %}
</ul>
