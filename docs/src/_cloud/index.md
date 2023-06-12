---
title: Meltano Cloud
description: Information about Meltano Cloud Concepts.
layout: doc
toc: false
hidden: false
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

With Meltano Cloud, data engineers can focus on high-value data work, and organizations can manage all their pipelines in one place, scale data volumes without cost concerns, and receive professional support for connectors and the Meltano SDK.

You build the pipelines, we manage the infrastructure. All of the flexibility, none of the hassle.

See [https://meltano.com](https://meltano.com) for more details on [pricing](https://meltano.com/pricing/) and the Meltano Cloud announcement [blog post](https://meltano.com/blog/introducing-meltano-cloud-you-build-the-pipelines-we-manage-the-infrastructure/).

## Getting Started

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
    ```

    Commit your changes back to the GitHub repository.

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

5. Next follow the [Onboarding Guide](/cloud/onboarding/) to configure your GitHub repository with Meltano Cloud.

Once your Meltano Cloud project is set up you can explore the Meltano Core [getting started guide](/getting-started/part1) to learn how to customize your project.


## Understanding Cloud Concepts

The following are the core concepts of Meltano Cloud.
You can find more details on each in the [Cloud Concepts](/cloud/concepts) documentation, or follow these links to find the concept you're looking for:
- [Users](/cloud/concepts#meltano-cloud-users)
- [Organizations](/cloud/concepts#meltano-cloud-organizations)
- [Projects](/cloud/concepts#meltano-cloud-proojects)
- [Deployments](/cloud/concepts#meltano-cloud-deployments)
- [Schedules](/cloud/concepts#meltano-cloud-schedules)
- [Pipelines](/cloud/concepts#meltano-cloud-pipelines)

## Usage

- [Cloud UI](/cloud/usage#cloud-ui)
- [Managing Projects](/cloud/cloud-cli#project)
- [Managing Deployments](/cloud/cloud-cli#deployment)
- [Managing Schedules](/cloud/cloud-cli#schedule)
- [Configuring Credentials](/cloud/cloud-cli#config)
- [Running Pipelines](/cloud/cloud-cli#run)
- [Managing Credits](/cloud/usage#managing-credits)
- [Limitations](/cloud/known_issues)
- [Notification Webhooks](/cloud/platform#job-or-schedule-run-notifications-via-webhook)
- [Backfills and State](/cloud/usage#backfills-and-state)


## References

- [Connectors](/cloud/connectors)
- [Cloud CLI](/cloud/cloud-cli)
- [Platform Info](/cloud/platform)
- [Security](/cloud/security)
