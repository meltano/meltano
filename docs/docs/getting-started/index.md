---
title: Meltano at a Glance
description: If you want to know why you should use Meltano, here's a quick overview of the basics of all of it.
layout: doc
sidebar_position: 1
---
## Meltano the Data Integration Engine

WTF is a "Data Integration Engine"? 

Let us explain: It's like a hammer, you can build dozens of different things with a hammer, but the hammer itself doesn't really care. It's just extraordinary at hammering in nails. The hammer also doesn't care who you are, it is optimized for hammering!

Meltano is extraordinarily great at giving you programmatic access to all the data you need in your products - whatever they are. Meltano is optimized to be in line with all software engineering best practices like versioning, testing, and CI/CD.

This document is intended to give you enough technical understanding of how Meltano works in the major different use cases people use it for today:

1. integrating 3rd party data sources into your existing product
2. building data-powered products based on internal data
3. setting up production data ingestion pipelines for machine learning
4. integrating into an internal data stack for BI & analytics

### What users say

_"For us it's a better day at work when we can use Meltano."_ - Nino Müller, Head of Technology at Substring

_"I love Meltano because it’s so pleasant to use with its DevOps and Everything-as-Code style. It is easy to set up, flexible, and integrates with pretty much any orchestrator as well as dbt (data build tool)"._ - Martin Morset

### Why companies love to build with Meltano

- **No lock-in**: It's open source and has a strong community, you'll always be free.. (derisk)
- **It's extensible from day 1**: It's super easy to add a custom connection using the SDKs/EDKs.
- **Amazing developer experience**: Developers go from start to finish on new data projects, including extraction, loading, transforming, & orchestrating data within days.
- **Small surface area**: Features like "inline data mappings" make it easy to remove unnecessary information from your data, and help companies stay compliant to security & GDPR regulations.

### The Quick Introduction 3rd party

## Core Workflow

Meltano helps you to create your end-to-end data stack within minutes. The core workflow depends on your data stack, but it will usually involve:

1. **Extracting data** from data sources & loading them into targets.
2. **Transforming data** inside a database.
3. **Orchestrating** the extract/load/transform process.
4. Adding **additional steps** to the process like testing the data inside transformations with dbt tests, using Great Expectations, running analyses inside Jupyter notebooks, visualizing data with Superset etc.

Meltano allows you to do any combination of these steps inside your Meltano project, controlled by the Meltano CLI.

...
### The Quick Introduction internal data heavy

...
### The Quick Introduction ML

...
### The Quick Introduction internal BI


### The Quick Introduction

Waiting to see how Meltano works within 90 secs? We got you covered:

<iframe class="video" src="https://www.youtube.com/embed/53WC4kTwbGU" title="From 0 to ELT in 90 seconds with Meltano, tap-gitlab, and target-postgres" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Core Workflow

Meltano helps you to create your end-to-end data stack within minutes. The core workflow depends on your data stack, but it will usually involve:

1. **Extracting data** from data sources & loading them into targets.
2. **Transforming data** inside a database.
3. **Orchestrating** the extract/load/transform process.
4. Adding **additional steps** to the process like testing the data inside transformations with dbt tests, using Great Expectations, running analyses inside Jupyter notebooks, visualizing data with Superset etc.

Meltano allows you to do any combination of these steps inside your Meltano project, controlled by the Meltano CLI.

### Extracting & Loading data

Here's a complete walk-through pulling data from AWS S3 and dumping it into a PostgreSQL database within 60 secs.

<div class="language-bash highlighter-rouge">
    <iframe class="video" src="https://www.youtube.com/embed/htbVZIR3tbs" title="How to Use Meltano in 60 Seconds" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

### Transforming data

Here's a complete walk-through extending the extract & load to include more CSVs and running a dbt-project over them to transform the data.

<iframe class="video" src="https://www.youtube.com/embed/pMZmBMeGe3U" title="How to Use Meltano in 5 Minutes" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

### Getting Started Resources

This was just a glance at why you should use Meltano. If you're now as excited to use Meltano as we are, we recommend you head over to the [Getting Started Tutorial](/getting-started/installation).

If you cannot find an answer to your question, there's always an active [Meltano Slack Community](https://meltano.com/slack) to help you out.



....

While Meltano is a declarative data integration engine, made for building data-powered features fast, one of the use cases has always been to use Meltano as an ELT platform.
