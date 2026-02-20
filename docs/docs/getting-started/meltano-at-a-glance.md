---
title: Meltano for ELT at a Glance
description: If you want to know why you should use Meltano, here's a quick overview of the basics of all of it.
layout: doc
sidebar_position: 1
---
## Meltano the Data Integration Engine for ELT?

While Meltano is a declarative data integration engine, made for building data-powered features fast, one of the use cases has always been to use Meltano as an ELT platform.

This document is intended to give you enough technical understanding of Meltano as ELT tool to become excited about it and want to use it! It won't teach you how to use it, we've got Tutorials & How To's for that. When you're ready to start your first Meltano project, we recommend you dive right into our Tutorial.

### What users say

<i>"For us it's a better day at work when we can use Meltano."</i> - Nino Müller, Head of Technology at Substring

<i>"I love Meltano because it’s so pleasant to use with its DevOps and Everything-as-Code style. It is easy to set up, flexible, and integrates with pretty much any orchestrator as well as dbt (data build tool)".</i> - Martin Morset

## Meltano at a glance

Welcome to your Open Source DataOps Infrastructure! With Meltano you can move your data with 10x the developer experience while also managing all of the data tools in your stack. With Meltano, you can collaboratively build and improve your ideal data platform like a software project; spinning up a service or tool (Singer connectors, Airflow, dbt, Great Expectations, Snowflake, etc) and easily configure, deploy, and manage it through a single control plane.

### Why companies love to build with Meltano

- **No lock-in**: It's open source and has a strong community, you'll always be free.. (derisk)
- **It's extensible from day 1**: It's super easy to add a custom connection using the SDKs/EDKs.
- **Amazing developer experience**: Developers go from start to finish on new data projects, including extraction, loading, transforming, & orchestrating data within days.
- **Small surface area**: Features like "inline data mappings" make it easy to remove unnecessary information from your data pipelines, and help companies stay compliant to security & GDPR regulations.

### Key Features of Meltano, developers will love

- **Start simple**: Meltano is pip-installable and comes in a prepackaged docker container, you can have your first ELT pipeline running within minutes.
- **DataOps out-of-the-box**: Meltano provides tools that make DataOps best practices easy to use in every project.
- **Integrates with everything**: 300+ natively supported data sources & targets, as well as additional plugins like great expectations or dbt are natively available.
- **Easily customizable**: Meltano isn't just extensible, it's built to be extended! The SDK for Singer Connectors & EDK for Meltano Components are easy to use. Meltano Hub helps you find all of the connectors and components created across the data community.
- **Mature system**: Developed since [2018](https://handbook.meltano.com/timeline), runs in production at large companies like GitLab, and currently powers over a million pipeline runs monthly.
- **First class ELT tooling built-in**: Extract data from any data source, load into any target, use inline maps to transform on data on the fly, and test the incoming data, all in one package.

<!-- ### The Quick Introduction

Waiting to see how Meltano works within 90 secs? We got you covered:

<iframe class="video" src="https://www.youtube.com/embed/53WC4kTwbGU" title="From 0 to ELT in 90 seconds with Meltano, tap-gitlab, and target-postgres" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

## Core Workflow

Meltano helps you to create your end-to-end data stack within minutes. The core workflow depends on your data stack, but it will usually involve:

1. **Extracting data** from data sources & loading them into targets.
2. **Transforming data** inside a database.
3. **Orchestrating** the extract/load/transform process.
4. Adding **additional steps** to the process like testing the data inside transformations with dbt tests, using Great Expectations, running analyses inside Jupyter notebooks, visualizing data with Superset etc.

Meltano allows you to do any combination of these steps inside your Meltano project, controlled by the Meltano CLI.

<!-- ### Extracting & Loading data

Here's a complete walk-through pulling data from AWS S3 and dumping it into a PostgreSQL database within 60 secs.

<div class="language-bash highlighter-rouge">
    <iframe class="video" src="https://www.youtube.com/embed/htbVZIR3tbs" title="How to Use Meltano in 60 Seconds" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div> -->

<!-- ### Transforming data

Here's a complete walk-through extending the extract & load to include more CSVs and running a dbt-project over them to transform the data.

<iframe class="video" src="https://www.youtube.com/embed/pMZmBMeGe3U" title="How to Use Meltano in 5 Minutes" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

### Orchestrating workflows

Meltano uses Airflow as orchestrator for the pipelines. It's as simple as adding Airflow as a plugin to your project and then running

```
meltano schedule add gitlab-to-postgres --extractor tap-gitlab --loader target-postgres --interval @daily
```

to add the schedule. Meltano also provides commands to start an Airflow instance to execute on these schedules. You can find out more about it in the [Orchestrate Data Section](https://docs.meltano.com/guide/orchestration).

<!-- ### Adding Additional Steps

Need to add additional steps to your data pipeline? Here's a complete setup also pulling in Superset as visualization tool.

<iframe class="video" src="https://www.youtube.com/embed/sL3RvXZOTvE" title="From 0 to DataOps - Meltano 2.0 Speedrun Demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

### Getting Started Resources

This was just a glance at why you should use Meltano. If you're now as excited to use Meltano as we are, we recommend you head over to the [Getting Started Tutorial](/getting-started/).

If you cannot find an answer to your question, there's always an active [Meltano Slack Community](https://meltano.com/slack) to help you out.
