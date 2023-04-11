---
title: "Meltano Cloud Fees"
layout: doc
hidden: true
---
<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Meltano Cloud Fees

_Last updated: April 10, 2023_

Unless specified otherwise in the applicable Order Form, the following terms and fees shall apply to the Cloud Service:

1. <u>Definitions</u>:
    - Additional Runtime: Runtime exceeding the Included Runtime.
    - Base Spend: In a Credit Purchase, the base price charged for the credits covered by the Credit Threshold.
    - Credit Purchase: A nonrefundable upfront purchase of Credits in bulk.
    - Credit Threshold: The minimum Credit Purchase size to receive the rates on the Service Consumption Table below.
    - Credit: A unit consumed by Pipeline Runs across the Organization. The number of Credits consumed by a given Pipeline Run is based on its Pipeline’s Frequency and its Additional Runtime. Credits can be purchased in bulk in a Credit Purchase, or be acquired as set forth in the Service Level Agreement. Credits are shared by all Projects in an Organization, and may not be redeemed for cash.
    - Deployment: A deployment on Meltano Cloud of a specific Environment and Project Git repository branch combination.
    - Environment: An environment defined in the Project. An Environment may have multiple Schedules and Deployments.
    - Frequency: The number of times a Pipeline Run of a Schedule’s Pipeline is to be executed in a specific Deployment during a given period based on the Schedule’s cron schedule expression, with a maximum of one Run every 15 minutes.
    - Frequent Run: A Pipeline Run of a Pipeline associated with a Schedule with a Frequency of 24 or more times per day.
    - Included Runtime: Runtime of a Pipeline Run that is not charged beyond the cost of the Pipeline Run itself: 10 minutes for Infrequent Runs, 5 minutes for Frequent Runs.
    - Incremental Spend: In a Credit Purchase, the price charged for each Credit in the next set of Credits (or portion of the next set of Credits) after surpassing the Credit Threshold.
    - Infrequent Run: A Pipeline Run of a Pipeline associated with a Schedule with a Frequency of less than 24 times per day, or a Pipeline Run triggered externally using the Meltano Cloud command line interface (CLI) or application programming interface (API).
    - Meltano Cloud: The Cloud Service for hosting Projects created using Meltano Core.
    - Meltano Core: The tool for building and running Pipelines available at https://github.com/meltano/meltano.
    - Order Form: Order Form: An ordering document or online order entered into between Customer and Meltano, or online order process completed by Customer and confirmed by Meltano, including any applicable terms, in each case specifying the Meltano Cloud service(s) to be provided.
    - Organization: The Customer’s top-level entity on Meltano Cloud. An Organization may have multiple Projects.
    - Pipeline Run: An execution of a Pipeline.
    - Pipeline: A named pipeline defined in the Project, or the tasks associated with a Schedule.
    - Project: A Git repository containing a meltano.yml file and other artifacts created using Meltano Core that is accessed and used by Meltano Cloud. A Project may have multiple Pipelines, Schedules, Environments, and Deployments.
    - Runtime: The cumulative execution time of all tasks in a Pipeline Run, from the start of the task to the end of the task, excluding platform startup and shutdown time.
    - Schedule: A schedule defined in the Project and enabled in a specific Deployment.

2. Credits are priced based on a diminishing slope: in other words, the more Pipelines Customer runs, the cheaper the incremental cost per unique Pipeline Run. Rates will be determined by the Service Consumption Table set forth below, subject to the terms of your specific Order Form. Meltano will provide Customer with monthly usage for the current and previous months via the Meltano Cloud CLI and dashboard.

3. When the Credits in Customer’s Organization are depleted, the Organization will no longer run Pipelines. When Credits are close to being depleted, Meltano Cloud will alert Customer. If Customer has a Credit Purchase that is coming to an end, Customer must contact Customer's account representative to arrange for a new purchase on an updated Order Form, or complete a Credit Purchase through Meltano Cloud.‍

4. <u>Service Consumption Table</u>:

    | Unit               | Consumption            |
    |--------------------|------------------------|
    | Infrequent Run     | 1 Credit               |
    | Frequent Run       | 0.5 Credits            |
    | Additional Runtime | 0.1 Credits per minute |

    Pricing of Credits is specified on Customer's Order Form. The table will be added to this page once Meltano Cloud is out of Beta.
