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

-  integrating 3rd party data sources into your existing product
-  building data-powered products based on internal data
-  setting up production data ingestion pipelines for machine learning
-  integrating into an internal data stack for BI & analytics

### What users say

_"For us it's a better day at work when we can use Meltano."_ - Nino Müller, Head of Technology at Substring

_"I love Meltano because it’s so pleasant to use with its DevOps and Everything-as-Code style. It is easy to set up, flexible, and integrates with pretty much any orchestrator as well as dbt (data build tool)"._ - Martin Morset

### Why companies love to build with Meltano

- **No lock-in**: It's open source and has a strong community, you'll always be free.. (derisk)
- **It's extensible from day 1**: It's super easy to add a custom connection using the SDKs/EDKs.
- **Amazing developer experience**: Developers go from start to finish on new data projects, including extraction, loading, transforming, & orchestrating data within days.
- **Small surface area**: Features like "inline data mappings" make it easy to remove unnecessary information from your data, and help companies stay compliant to security & GDPR regulations.

### The Quick Introduction 3rd party use cases

Meltano helps you to integrate 3rd party data into your already existing products. 

The core workflow will usually involve:

- **Extracting data** from data sources using our 600+ connectors loading it either into memory (e.g. using duckDB), some local storage (JSONL, CSV) or onto 
a data lake. 

- **Processing data** Either using your already existing code base, or with a Meltano-powered Python script. 


### The Quick Introduction internal data heavy internal data

Meltano helps you to integrate your own data into products.

The core workflow will usually involve:

- **Extracting data** from a few selected data sources. 

- **Replicating the same extraction process** for 100s or 1,000s of customers with slight variations, different configs, different auth credentials,...

- **Storing the data** in a database or a data lake.


...
### The Quick Introduction ML

...
...
### The Quick Introduction internal BI

...
Meltano helps you to create your end-to-end data stack within minutes. The core workflow depends on your data stack, but it will usually involve:

- **Extracting data** from data sources & loading them into targets.
- **Transforming data** inside a database.
- **Orchestrating** the extract/load/transform process.
- Adding **additional steps** to the process like testing the data inside transformations with dbt tests, using Great Expectations, running analyses inside Jupyter notebooks, visualizing data with Superset etc.

Meltano allows you to do any combination of these steps inside your Meltano project, controlled by the Meltano CLI.

<iframe class="video" src="https://www.youtube.com/embed/53WC4kTwbGU" title="From 0 to ELT in 90 seconds with Meltano, tap-gitlab, and target-postgres" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>