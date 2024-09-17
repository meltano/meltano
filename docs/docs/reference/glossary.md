---
title: Glossary
description: A glossary of terms used in the Meltano documentation.
layout: doc
sidebar_position: 5
---

## [Bookmarks](#bookmarks)

In a Singer extract-load pipeline, the work 'bookmark' is used to refer to the tracking artifact for a single stream. The state for any given tap likely contains many bookmarks, generally one bookmark per stream.

## [CI/CD](#cicd)

CI/CD is a method to frequently deliver apps to customers by introducing automation into the stages of app development. [Learn more...](https://www.redhat.com/en/topics/devops/what-is-ci-cd)

## [DAG](#dag)

DAG means Directed Acyclic Graph. Within data workflows, any sequence of tasks can be represented as a DAG when the individual tasks are linked. This is done explicitly in dbt via the "ref" function.

## [DataOps](#dag)

DataOps brings the benefits of DevOps best practices to the data lifecycle. [Learn more...](https://meltano.com/dataops/)

## [ELT](#elt)

ELT means Extract, Load, Transform. It is a method of data replication and transformation used to perform data integration at any scale. The purpose of ELT is to extract specific data, such as customer information or billing records, from its source, and deliver it to its end point in the fastest, most reliable way possible. [Learn more...](https://meltano.com/meltano-elt/)

## [.env File](#env-file)

.env (pronounced "dot ehnv") files allow you to configure environment variables within an application. This is useful for passing credentials and secrets to an app without so that you don't need to check passwords or keys into version control.

## [Docker](#docker)

Docker is a tool that packages software into distributable/reproducible units called containers that contain most of what the software needs to run including libraries, system tools, code, and runtime. [Learn more...](https://www.docker.com/)

## [Docker Image](#docker-image)

A Docker image contains application code, libraries, tools, dependencies and other files needed to make an application run. [Learn more...](https://docs.docker.com/engine/reference/commandline/image/)

## [Docker Container](#docker-container)

A Docker container image is a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries and settings. [Learn more...](https://www.docker.com/resources/what-container/)

## [Orchestration](#orchestration)

Orchestration refers to the sequencing and running of any tasks. Orchestrators are responsible for running tasks at specified times and handling advanced features like retries. [Learn more...](https://docs.meltano.com/guide/orchestration)

## [Python Virtual Environment](#python-virtual-environment)

A virtual environment is a Python environment such that the Python interpreter, libraries and scripts installed into it are isolated from those installed in other virtual environments, and (by default) any libraries installed in a “system” Python, i.e., one which is installed as part of your operating system. [Learn more...](https://docs.python.org/3/library/venv.html)

## [Singer](#singer)

An open source specification for sending and receiving data. Unlike other similar standards, the Singer specification handles incremental use cases and is optimized for data replication use cases like the ones in ELT and data engineering workloads. [Learn more...](https://hub.meltano.com/singer/spec)

## [State](#state)

In Singer extract-load pipelines, the word 'state' is used to refer to progress trackers and artifacts that enable incremental replication. The state for a tap is a JSON object contain the set of bookmarks that track the resume-point for all streams being replicated.

## [Streams](#streams)

In the Singer ecosystem, a stream typically represents a table, API endpoint, or discrete set of data. [Learn more...](https://hub.meltano.com/singer/spec)

## [Stream Map](#stream-map)

In the Singer ecosystem, a stream map is an inline transformation that is applied to data on the fly before it arrives at a target. [Learn more...](https://sdk.meltano.com/en/latest/stream_maps.html)

## [Tap](#tap)

In Singer extract-load pipelines, the word tap is synonymous with extractor. This is the plugin that defines how data should be read from the source system.

## [Target](#target)

In Singer extract-load pipelines, the word target is synonymous with loader. This is the plugin that defines how data should be written to the destination.

## [Transformation](#transformation)

Data transformation in a modern DataOps platform is a reproducible data shaping process that does not modify source data. Data transformation occurs after EL (extract-load) operations have been executed. Data is shaped or "transformed" into more usable datasets, according to the business logic and use cases which are most valuable to the audience.
