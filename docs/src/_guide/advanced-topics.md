---
title: Advanced Topics
description: Learn about advanced topics in the Meltano.
layout: doc
weight: 10
---

## Installing Optional Components

Most of Meltano's features are available without installing any additional packages. However, some niche or environment-specific features require the installation of [Python extras](https://peps.python.org/pep-0508/#extras). The following extras are currently supported:

* `mssql` - Support for Microsoft SQL Server
* `s3` - Support for using S3 as a [state backend](/concepts/state_backends)
* `gcs` - Support for using Google Cloud Storage as a [state backend](/concepts/state_backends)
* `azure` - Support for using Azure Blob Storage as a [state backend](/concepts/state_backends)
