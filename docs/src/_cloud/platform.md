---
title: "Platform Information"
layout: doc
hidden: true
---

# Meltano Cloud

> Meltano Cloud is currently in Alpha. Features and implementation details may change between Alpha and GA.

## Cloud Platform

Meltano Cloud currently runs on AWS.

## Region

The primary AWS region hosting Meltano Cloud is `us-west-2` (Oregon, US).

Future plans include expanding into an EU region (timing is TBD).

## IP Addresses

We use the following IP addresses for all egress traffic.
Add the following IPs to your allow list if your Meltano Cloud workload requires access to your protected servers.

```
54.68.17.185/32
44.231.17.56/32
44.225.129.236/32
```

## Reserved Variables

There are specific environment variables that are reserved for certain use-cases.

### SSH Private Keys for Private Git Repository Package Access

`GIT_SSH_PRIVATE_KEY` is a reserved variable that should be set if you have private repository packages.

To encrypt, set the ssh private key env variable into your `.env` file as-is in the private key file with single quotes
around them.

Example `.env` file to be encrypted:

```
GIT_SSH_PRIVATE_KEY='-----BEGIN OPENSSH PRIVATE KEY-----
therearelotsofprivatekeymaterialhere
onvariouslineslikethis
wecanjustcopypasteasitappearsinthefile
andusesinglequotesaroundthewholething
-----END OPENSSH PRIVATE KEY-----'
SOME_OTHER_SECRET=1234asdf
```

Then continue with encryption using the [kms-ext](https://github.com/meltano/kms-ext) utility.

## Roles and Permissions

### Role descriptions

- Users with the `owner` role access can create and delete projects, as well as performing all functions of `maintaner`. Owners can also view billing history and perform other account management functions, such as adding new users.
- Users with the `maintaner` role access can perform normal development and maintenance functions, such as updating schedules and executing jobs. Maintainers cannot add or delete projects or users.
- Users with the `reader` role only have read-only access: for instance, to view job statuses and summary logs.

### Future updates

Note:

- More advanced role-based access permissions may be added in future versions on Meltano Cloud.
