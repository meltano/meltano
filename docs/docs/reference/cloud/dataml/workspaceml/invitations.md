---
title: Invitations
description: Reference documentation for workspace invitation customisation.
permalink: /dataml/workspaceml/invitations/
nav_order: 1
parent: WorkspaceML
grand_parent: DataML
---

# {{page.title}}

---

Invitations allow you to customise the onboarding experience for new members of your workspace.
{: .fs-5 }

---

## Result URL

`INVITATION_EMAIL_RESULT_URL`

The URL a user will be redirected to after accepting the workspace invitation.

```yaml
app_properties:
  INVITATION_EMAIL_RESULT_URL: https://meltano.com/slack
```

## Subject

`INVITATION_EMAIL_SUBJECT`

The subject of the invitation email. Templating is not yet supported (as defined below).

```yaml
app_properties:
  INVITATION_EMAIL_SUBJECT: You have been invited to a workspace
```

## Template

`INVITATION_EMAIL_TEMPLATE`

The invitation email template HTML, processed by [Thymeleaf](https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html).

```yaml
app_properties:
  INVITATION_EMAIL_TEMPLATE: |-
    <!DOCTYPE html>
    <html xmlns:th="http://www.thymeleaf.org">
    <head>
    </head>
    <body>
      <h2 th:inline="text">[[${invitationCreatorName}]] ([[${invitationCreatorEmail}]]) has
        invited you to the '[[${workspaceName}]]' Workspace.</h2>

      <p>
        <a th:href="${passwordResetTicketUrl}">Accept invitation</a>
      </p>

      <br />
      <hr style="border: 2px solid #EAEEF3; border-bottom: 0;" />
    </body>
    </html>
```

### Variables

Name | Description
--- | ---
`invitationCreatorName` | The name of the invitation creator profile
`invitationCreatorEmail` | The email of the invitation creator profile
`workspaceName` | The name of the workspace invited to
`passwordResetTicketUrl` | The link to accept the invitation (this should be accessible for a user to be able to accept)

We recommend [inlining](https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#inlining) when using variables, where possible (see above example).
