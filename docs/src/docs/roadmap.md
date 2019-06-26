# Roadmap

## Milestones

You can track our progress through [ our milestones](https://gitlab.com/groups/meltano/-/milestones).

## Release

Meltano currently follows a weekly release schedule.

For our recent changes, you can check [our CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md). 

## MAUI

The focus of our team is to grow [MAUI](#maui) by 10% every week. We track the Monthly Active Users (MAU) of three things to understand the health of our user adoption funnel from first impression to fully onboarded user:

1. [Meltano.com Website](https://meltano.com)
2. [Meltano Command Line Interface - CLI](https://meltano.com/docs/meltano-cli.html)
3. [Meltano UI](https://meltano.com/docs/architecture.html#meltano-ui)

The MAU of the UI are called MAUI, this is pronounced like [the island](https://en.wikipedia.org/wiki/Maui).

Internal metrics:

1. [Google Analytics for MAUI](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192645310p188384771/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)
2. [Google Analytics for CLI MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192718180p188392047/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D/)
3. [Google Analytics for Meltano.com Website MAU](https://analytics.google.com/analytics/web/?utm_source=marketingplatform.google.com&utm_medium=et&utm_campaign=marketingplatform.google.com%2Fabout%2Fanalytics%2F#/report/visitors-actives/a132758957w192515807p188274549/_u.date00=20190209&_u.date01=20190308&active_users.metricKeys=%5B0,1,2,3%5D)

## Focus

The focus of our team is to grow [MAUI](#maui) by 10% every week.
A week is measured from Sunday to Saturday.
Every improvement we make should be optimized by that.
This means sometimes we should prioritize promotion (blog, twitter, video, talk) and usability (docs, UX) over new features.

## Monetization

We are building Meltano to solve a problem that software companies share: How to acquire the highest-value customers at the lowest cost of acquisition? 

We are solving this problem by incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers. Next, we will focus on building a community around Meltano with more users and regular contributors to the code base.

Right now Meltano is open source. In the future we'll introduce proprietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. An example of a proprietary/source available feature is fine grained access controls. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

## Personas

Meltano provides tools to help data teams manage their end-to-end pipeline. This process usually involves collaboration between software engineers and data analysts. In the personas below, we have begun to capture our insights revealed from user interviews.

Ultimately, we are looking to help Meltano users successfully complete a wide range of user stories. To help users onboard quickly, we have created some [simple user stories](https://docs.google.com/document/d/1axKIKtC65Zf9yAV6pApwbZD6Hml-EPh7HEg7W-fPbg0/edit) and we are working to support them through our tutorials.

### Eric the Data Engineer

#### At a Glance

Age: 38

Location: Albany, NY

Life stage: Married, two young kids

Job Title: Data Engineer

Alternative Titles:  Business Intelligence Engineer, Software Developer

#### Job Summary

I am responsible for designing, constructing, installing, testing and maintaining highly scalable data management systems. I improve data foundational procedures, guidelines and standards. I work on  integrating new data management technologies and software engineering tools into existing structures. I also create custom software components and analytics applications.

#### Motivations

* When I build data pipelines, I want to know the uptime, so I make sure they are well crafted.
* When I share data, it should be usable, so the data analyst can integrated.
* When I don’t have to build custom solutions and instead use reliable solutions I can be more proactive.
* When all of my solutions are flexible, I can easily adapt them to the changing needs of the business.

#### Frustrations

* I’m frustrated when the tools are not reliable because this means the data does not move consistently.
* It is hard for me to maintain the management system when there is a problem with the foundation.

### Allie the Data Analyst

#### At a Glance

Age: 32

Location: NYC, NY

Life stage: Married, no children

Job Title: Data Analyst

Alternative Titles:  Data Scientist - Analytics, Business Intelligence Engineer, Full Stack Data Analyst, Business Analyst

#### Job Summary

I am responsible for retrieving and gathering data from data warehouse, organizing it and making the data collected insightful and easy to understand.  My goal is to help stakeholders make informed decisions for their business.

#### Motivations

* When collaborating with others, I want to receive and create clear requirements so I am able to execute and deliver a precise presentation.
* When I ask the right questions, I am more effective in communicating usable data. 
* When I develop automated and reusable routines, I am confident in the quality of my pipelines and be more effective in my role.
* When I create meaningful reports, management has insights about new trends as well as areas the company may need to improve upon.

#### Frustrations

* I’m frustrated when I have to educate stakeholders on the meaning of data in their business expertise because it’s a symptom of lack of data adoption from an organization. 
* I’m frustrated when data integrity is compromised because data becomes fragmented and full of holes and stakeholders no longer trust my analysis.
* It is hard to interprete data when I may not have the right data because I am unable to support my conclusions.