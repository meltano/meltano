---
title: "Security"
description: Details the security stature of Meltano Cloud
layout: doc
weight: 3
---
# Meltano Cloud - Security Whitepaper

> **Note**
> Meltano Cloud is currently in Alpha. Features and implementation details may change between Alpha and GA.

## Securing Project Secrets

"Project secrets" are any credentials or secrets required for executing the project's ELT functions. Project secrets are encrypted using the customer organization's dedicated public encryption key before submitting to Meltano.

### Credential security FAQ

#### How are secrets protected?

1. Project secrets will always be encrypted, in transit and at rest.
1. Meltano will never store your secrets in clear text.
1. Meltano engineers do not have access to directly decrypt your secrets.
1. The decryption key for project secrets will never leave AWS servers.
1. Our IAM policies only allow the `decrypt` action within containers that are running project workloads.

##### What encryption algorithms are used?

The algorithm for encrypting secrets is an RSA assymetric encryption, using 4096-bit keys.

More information is available on the AWS website:

- https://docs.aws.amazon.com/kms/latest/developerguide/asymmetric-key-specs.html#key-spec-rsa-encryption
