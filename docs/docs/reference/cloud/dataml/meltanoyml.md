---
title: meltano.yml
description: Reference documentation for meltano.yml
permalink: /dataml/meltanoyml/
nav_order: 7
parent: DataML
---

# {{page.title}}

---

Reference documentation for Meltano files.
{: .fs-5 }

[Meltano](https://meltano.com/) is a data automation tool and used to manage data plugins in [workspaces]({{site.baseurl}}/api/resources/workspaces). 
{: .fs-5 }

The [meltano.yml](https://docs.meltano.com/concepts/project#meltanoyml-project-file) file is where your workspace, a Meltano project, will store information about your data sources, [data stores]({{site.baseurl}}/dataml/datastoreml) and any other plugins used in your workspace.
{: .fs-5 }

---

### Example: `meltano.yml`

```yaml
version: 1
send_anonymous_usage_stats: true
project_id: 1234567890-abc
plugins:
  extractors:
  - name: tap-spotify
    pip_url: git+https://github.com/Matatika/tap-spotify@v0.3.0
  loaders:
  - name: target-postgres--transferwise
    variant: transferwise
    pip_url: git+https://github.com/Matatika/pipelinewise-target-postgres@v0.1.0
  transforms:
  - name: dbt-spotify
    variant: spotify
    pip_url: https://github.com/Matatika/dbt-tap-spotify@v0.3.0
  transformers:
  - name: dbt
    pip_url: dbt==0.20.2
  files:
  - name: analyze-spotify
    pip_url: git+https://github.com/Matatika/analyze-spotify@v0.4.0
  - name: files-dbt
    pip_url: git+https://github.com/Matatika/files-dbt@v1.0.x.0
```

---

Further Reading: 

- [Meltano Documentation](https://docs.meltano.com/)
- [Meltano's meltano.yml documentation](https://docs.meltano.com/concepts/project#meltanoyml-project-file)
