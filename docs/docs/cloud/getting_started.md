---
title: "Getting Started (Cloud)"
description: Cloud Getting Started Guide
layout: doc
sidebar_position: 1
sidebar_class_name: hidden
---

:::info

<p><strong>Meltano Cloud is currently in Beta.</strong></p>
<p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>

:::

### Existing Meltano Project

If you already have a Meltano project you can go straight to the [onboarding guide](/cloud/onboarding/) to configure your GitHub repository with Meltano Cloud.

### New to Meltano

Meltano Cloud connects to an existing Meltano project in your GitHub repository, so if you don't yet have a Meltano repository set up you can do the following:

1. Create a [GitHub repo](https://docs.github.com/en/get-started/quickstart/create-a-repo)

2. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the repo locally

3. Initialize Your Meltano Project

   Using the [`init` command](/reference/command-line-interface#init) you can create the scaffolding for your project, just choose a name:

   ```bash
   meltano init <INSERT_YOUR_PROJECT_NAME>
   cd <INSERT_YOUR_PROJECT_NAME>
   ```

4. Add Sample Plugins and Schedules

   The following configuration snippet can be added to your `meltano.yml` file located in your new project directory.
   The configuration includes a sample extractor and loader with an associated job and schedule:

   ```yaml
   plugins:
     extractors:
     - name: tap-smoke-test
       variant: meltano
       pip_url: git+https://github.com/meltano/tap-smoke-test.git
       config:
         streams:
         - stream_name: animals
           input_filename: https://raw.githubusercontent.com/meltano/tap-smoke-test/main/demo-data/animals-data.jsonl
     loaders:
     - name: target-jsonl
       variant: andyh1203
       pip_url: target-jsonl
   jobs:
   - name: sample_job
     tasks:
     - tap-smoke-test target-jsonl
   schedules:
   - name: sample_schedule
     interval: 0 0 * * *
     job: sample_job
   ```

5. Lock your new plugins and commit the changes

   ```bash
   meltano lock --update --all
   ```

   Commit your changes back to the GitHub repository.


6. Next follow the [Onboarding Guide](/cloud/onboarding/) to configure your GitHub repository with Meltano Cloud.

Once your Meltano Cloud project is set up you can explore the Meltano Core [getting started guide](/getting-started/part1) to learn how to customize your project.
