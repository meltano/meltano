---
title: Role-based Access Control (alpha)
description: Learn about roles.
layout: doc
---

<div class="notification is-danger">
  <p>This feature is experimental and subject to change.</p>
</div>

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

## User Authentication

You should see the following login page whenever you open Meltano.

![Meltano Login](images/role-based-access-control/meltano-login.png)

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

- _department.resource-name_
- _topic.resource-name_
- _access-level.resource-name_
