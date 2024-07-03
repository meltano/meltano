---
title: "Meltano Cloud Service Level Agreement"
layout: doc
sidebar_class_name: hidden
---

:::info

<p><strong>Meltano Cloud has been shut down in favor of Arch.</strong></p>
<p>Read the announcement on <a href="https://meltano.com/blog/were-bringing-powerful-data-engineering-capabilities-to-software-teams-with-arch/">our blog</a>.</p>

:::

## Meltano Cloud Service Level Agreement (SLA)

_Last updated: April 10, 2023_

Unless specified otherwise in the applicable Order Form, the following terms and fees shall apply to the Cloud Service:

1. <u>Definitions</u>:

   - Average Run Credits: The average number of Credits consumed by the Schedule’s most recent Consecutive Successful Runs.
   - Consecutive Successful Runs: 5 consecutive Successful Runs over at least 5 consecutive days since the last time the Pipeline’s configuration, or that of any of its tasks, was changed.
   - Credit: A unit consumed by Pipeline Runs across the Organization. Credits can be purchased in bulk, or be acquired as set forth in this Service Level Agreement. Credits are shared by all Projects in an Organization, and may not be redeemed for cash.
   - Deployment: A deployment on Meltano Cloud of a specific Environment and Project Git repository branch combination.
   - Downtime: Calculated as “Missed Ticks / Monthly Ticks” during a calendar month. The inverse of Uptime.
   - Emergency Maintenance: Downtime outside of Scheduled Downtime hours due to the application of urgent patches or fixes, or other urgent maintenance, recommended by Meltano’s vendors to be applied as soon as possible.
   - Environment: An environment defined in the Project. An Environment may have multiple Schedules and Deployments.
   - Meltano Cloud: The Cloud Service for hosting Projects created using Meltano Core.
   - Meltano Core: The tool for building and running Pipelines available at https://github.com/meltano/meltano.
   - Missed Tick: A Tick of an enabled Working Schedule that did not result in a Successful Run starting within 30 minutes or before the next Tick. If the first Run for a Tick was not a Successful Run, the system may attempt a retry Pipeline Run within 30 minutes after the Tick time, which will not consume additional Credits.
   - Monthly Ticks: Total number of Ticks for a given Schedule during a calendar month, taking into account changes to the Schedule’s cron schedule expression during that month.
   - Organization: The Customer’s top-level entity on Meltano Cloud. An Organization may have multiple Projects.
   - Pipeline Run: An execution of a Pipeline.
   - Pipeline: The tasks associated with a Schedule.
   - Project: A Git repository containing a meltano.yml file and other artifacts created using Meltano Core that is accessed and used by Meltano Cloud. A Project may have multiple Pipelines, Schedules, Environments, and Deployments.
   - Run: A Pipeline Run triggered as a result of a Tick.
   - Schedule: A schedule defined in the Project and enabled in a specific Deployment.
   - Scheduled Downtime: Downtime during the hours of 6:00 p.m. to 8:00 p.m. Thursday U.S. Pacific Time.
   - Successful Run: A Run that completed successfully, or that failed for a reason unrelated to the Meltano Cloud platform (e.g., misconfiguration or a source API issue).
   - Tick: Each time a Run of a Schedule’s Pipeline is to be executed in a specific Deployment based on its cron schedule expression, with a maximum of one Tick (and Run) every 15 minutes.
   - Trial Period: The period of time that Customer first has access to and uses Meltano Cloud for evaluation or trial without a paid contract in place as specified in the applicable agreement.
   - Uptime: Calculated as “(Monthly Ticks - Missed Ticks) / Monthly Ticks” during a past calendar month.
   - Working Schedule: A Schedule that has had Consecutive Successful Runs.

2. <u>Service Level Commitment and Credits</u>. If Uptime of a given Working Schedule falls below 99.9%, then for every Missed Tick of that Schedule, Customer’s Account shall be credited 2 times the Average Run Credits, which may be used solely for future Pipeline Runs. Credits given for Downtime may not exceed 50% of the Average Run Credits multiplied by the Schedule’s Monthly Ticks for the month in question and may not be redeemed for cash.

3. <u>Exceptions</u>. The above service level commitment and Credits do not apply to Scheduled Maintenance or circumstances where the Cloud Service is affected by operational, connectivity or other service interruptions beyond Meltano’s sole control, including without limitation:

   - Maintenance requested by Customer or Emergency Maintenance;
   - Outages created or experienced by vendors and infrastructure partners;
   - The Customer’s inability to deliver required content to Meltano or its vendors in a timely manner;
   - Interruptions due to changes requested by the Customer and agreed in advance as potentially disruptive to the Cloud Service;
   - Events caused either directly or indirectly by acts, errors or omissions by Customer, its agents, vendors or end-users, including but not limited to negligence, willful misconduct or breach of the Agreement;
   - Customer’s own inability to connect due to issues with their ISP, local settings or circumstances;
   - Events arising from malicious, unlawful or terrorist acts against Customer, Meltano or their employees, contractors, vendors or property including viruses, Trojan Horses, and other malware; and
     -Disasters and events force majeure such as natural disasters, flood, earthquake, war, tornados, extended power outages.

4. <u>Exclusions</u>. The above service level commitment and Credits do not apply to any services or data that are not expressly listed in the CSA, whether implied or inferred, nor do they apply to performance issues caused by Customer's equipment or third-party equipment. The above service level commitment and Credits do not apply during a Trial Period.

5. <u>Claiming Credits</u>. To receive any Credits, Customer must notify Meltano in writing within 30 days after Customer becomes eligible to receive a Credit. Failure to comply with this requirement will forfeit Customer's right to receive a Credit.

6. <u>Limitations</u>. The remedies provided herein for interruptions in Cloud Service shall apply only while the Customer is in good standing and not in breach of any term of the Agreement, and the Customer accounts are paid in full with no amounts past due or security deposits not fully paid.

7. <u>Maintenance Announcements</u>. From time to time, Meltano will make announcements via email regarding maintenance activities (“Maintenance Announcements”) which may affect the Cloud Service, including without limitation the possibility of affecting the Uptime of the Cloud Service. Maintenance Announcements are Meltano’s sole method and requirement for communication of such activities to Customer hereunder. It is the Customer’s responsibility to subscribe to, remain aware of and adjust as necessary to the content and effect of the Maintenance Announcements.

8. <u>Maintenance Activities</u>. Meltano will use reasonable commercial efforts to schedule maintenance activities that may result in likely, imminent, or limited interruptions in the Cloud Service, not less than 48 hours in advance of the beginning of that activity. Meltano may determine at its sole discretion that Emergency Maintenance is necessary to protect or preserve the integrity of its services or infrastructure, which may affect Uptime of the Cloud Service, at which time Meltano will make a Maintenance Announcement when the maintenance is performed.
