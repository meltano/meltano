# Security & Privacy

## Introduction

When using Meltano, like any data science tool, it is important to consider the security and privacy implications.

- Meltano expects the required credentials for each extractor to be stored as a project variable. Project members with the role [`Maintainer` or `Owner`](https://docs.gitlab.com/ee/user/permissions.html#project-members-permissions) will be able to see these in plaintext, as well as any instance wide administrators. If you are using GitLab.com, this includes select GitLab employees responsible for the service.
  - Support for KMS systems is being considered for a future release.
- Because these variables are passed to GitLab CI jobs, it is possible to accidentally or maliciously compromise them:
  - For example, a developer who normally cannot see the variables in project settings, could accidentally print the environment variables when debugging a CI job, causing them to be readable by a wider audience than intended.
  - Similarly it is possible for a malicious developer to utilize the variables to extract data from a source, then send it to an unauthorized destination.
  - These risks can be mitigated by [restricting the production variables](https://docs.gitlab.com/ee/ci/variables/#protected-variables) to only protected branches, so code is reviewed before it is able to run with access to the credentials. It is also possible to set job logs to be available to only those with `Developer` roles or above, in CI/CD settings.
- When designing your data warehouse, consider any relevant laws and regulations, like GDPR. For example, historical data being retained as part of a snapshot could present challenges in the event a user requests to be forgotten.

## Personally Identifiable Information

It is important to be cognizant of the personally identifiable information which is extracted into the data warehouse. Warehouses are at their best when they are leveraged across many parts of the organization, and therefore it is hard to predict which users will ultimately have access and how each user will treat the data.

We recommend the following best practices:

1. Avoid extracting any personally identifiable information in the first place. For example, consider extracting only company names from your CRM and avoid extracting individual contact details.
1. If it is important to collect data about individual users, for example, to learn more about user behavior, pseudonymize the data prior to writing it into the data warehouse.
1. Consider how you are persisting any PII data, and its impact on compliance requirements like GDPR.

## Meltano Data Security and Privacy at GitLab

We take user security and privacy seriously at GitLab. We internally use Meltano to learn about how users interact with GitLab.com, build a better product, and efficiently run our organization. We adhere to the following guidelines:

1. GitLab employees have access to the data warehouse and can see pseudonymized data. In some cases due to public projects, it is possible to tie a pseudonymized account to a public account. It is not possible to learn the private projects a user is working on or contents of their communications.
1. We will never release the pseudonymized dataset publicly, in the event it is possible to reverse engineer unintended content.
1. Select GitLab employees have administrative access to GitLab.com, and the credentials used for our extractors. As noted above, developers on the Meltano project could maliciously emit credentials into a job log, however, the logs are not publicly available.

## Role Based Access Control (RBAC) <sup>ALPHA</sup>

::: danger IMPORTANT
This feature is experimental and subject to change.
:::

In the current architecture of Meltano, authorization is technically always enabled because every installation of Meltano comes with a single user that has administrative rights to everything. In other words, there are no restrictions as far as what the user can do and there is no difference between users who are logged in to Meltano.

While this functionality is still in alpha, you can enable RBAC by setting the environment variable `MELTANO_AUTHENTICATION` to `true`.

```bash
# Set in your .env file
export MELTANO_AUTHENTICATION=true
```

Now you can start your Meltano installation with:

```bash
meltano ui
```

### User Authentication

You should see the following login page whenever you open Meltano.

![](/screenshots/meltano-login.png)

There are two primary ways to authenticate:

1. Local user registration through the Register link
1. Authentication through a GitLab account

## Managing Roles

Meltano uses a RBAC (role-based access control) to expose resources to the current authenticated user.

- User: associated to an email, serves as the primary identity
- Role: associated to users, serves as the authorization source
- Permission: associated to roles, express the authorization scope
- Resource: Any `Design`, `Report`, `Dashboard`

In this system, any permission is assigned a "Context" which represent a pattern upon which resources will be tested for. Currently, the context tests for the `name` attribute of resources.

Here's an example, let's say we have a `Design` named `finance.month_over_month` and a `Permission` with a context `finance.*`, then this `Design` would be available to all users that have any role having this `Permission`.

This system allows you to create any kind of hierarchical system:

- *department.resource-name*
- *topic.resource-name*
- *access-level.resource-name*