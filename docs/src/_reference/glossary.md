---
title: Glossary
description: A glossary of terms used in the Meltano documentation.
layout: doc
---

{% for item in site.data.glossary %}

<h2>{{ item.term }}</h2>

<p>{{ item.definition }}
{% if item.link %}
<a href="{{ item.link }}">Learn more...</a>
{% endif %}
</p>

{% endfor %}
