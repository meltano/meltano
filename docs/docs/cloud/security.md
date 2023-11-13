---
title: "Security"
description: Details the security stature of Meltano Cloud
layout: doc
sidebar_position: 6
sidebar_class_name: hidden
---

:::info

<p><strong>Meltano Cloud is currently in Beta.</strong></p>
<p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>

:::

:::info

  <p>Meltano Cloud is currently in Beta. Features and implementation details may change between Beta and GA.</p>
:::

## Securing Project Secrets

"Project secrets" are any credentials or secrets required for executing the project's ELT functions. Project secrets are encrypted using the customer organization's dedicated public encryption key before submitting to Meltano.

### Credential security FAQ

#### How are secrets protected?

1. Project secrets will always be encrypted, in transit and at rest.
1. Meltano will never store your secrets in clear text.
1. Meltano engineers do not have access to directly decrypt your secrets.
1. The decryption key for project secrets will never leave AWS servers.
1. Our IAM policies only allow the `decrypt` action within containers that are running project workloads or for services that require specific secrets to perform tasks such as sending notifications to your webhook urls.
1. Meltano uses envelope encryption strategy with AWS KMS keys to encrypt your secrets.

##### What encryption algorithms are used?

The algorithm for encrypting secrets is an AES symmetric encryption, using 256-bit AES-GCM encryption keys.

More information is available on the AWS website:

- [Symmetric Encryption Keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#symmetric-cmks)

## Meltano Cloud GitHub App Permissions

### Meltano Cloud Login

When performing login to Meltano Cloud, either via the CLI or the web UI, the Meltano Cloud GitHub App will request only the following permissions:

- Read-only access to your email addresses

### Meltano Cloud Project Permissions

When adding a project to Meltano Cloud, you will need to install the GitHub App to your Organization in GitHub.
You may grant the GitHub App read-only permissions to only the repositories you require it to access.
The following permissions are provided to the Meltano Cloud GitHub App:

Repository Permissions

- Repository contents, commits, branches, downloads, releases, and merges (read-only)
- Search repositories, list collaborators, and access repository metadata (read-only)

Organization Permissions

- Organization members and teams (read-only)

Account Permissions

- Manage a user's email addresses (read-only)
