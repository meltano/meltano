---
metaTitle: The Meltano Project
description: At the core of the Meltano experience is the Meltano project, which represents the single source of truth regarding your data pipelines.
---

# The Meltano Project

<!-- The following is reproduced in docs/src/README.md#meltano-init -->

At the core of the Meltano experience is the Meltano project,
which represents the single source of truth regarding your data pipelines:
how data should be [integrated](/docs/integration.html) and [transformed](/docs/transformation.html),
how the pipelines should be [orchestrated](/docs/orchestration.html),
and how the various components should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init).

### Settings

To learn about project-specific settings, refer to the [Settings reference](/docs/settings.html#your-meltano-project).
