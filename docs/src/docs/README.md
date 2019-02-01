# Introduction

Meltano is an open source convention over configuration product for the whole data life cycle, all the way from loading data to analyzing it. It also leverages open source and software development best practices including:

- Version control
- Consistent primitives and naming schema
- Clear and powerful command line interface
- Continuous integration and deployment
- Making it easy to get started with up to date documentation

[![Meltano Diagram](/meltano-diagram.png)](/meltano-diagram.png)

Meltano stands for the steps of the data life cycle:

- Model
- Extract
- Load
- Transform
- Analyze
- Notebook
- Orchestrate

To empower you and your team in this life cycle, Meltano manifests as two tools:

1. command line interface (CLI)
1. web app (GUI)

These two tools enable you and your team to use Meltano in a few different ways:

1. Meltano as **Project** (CLI + GUI)
    - From data extraction to analysis and visualization with orchestration for automating the process
1. Meltano as **Framework** (CLI)
    - Helps you create and test extractors, loaders, and transforms
1. Meltano as **ELT** only (CLI)
    - Runtime for extracting, loading, and transforming of data
1. Meltano as **UI** only (GUI)
    - Interactively query, explore, visualize, and model the data (warehouse)

In addition, Meltano allows you to utilize the following tools for various steps of the data life cycle:

- **Collections**, Extract, Load, Transform: Meltano CLI
- **Designs**: Superset or Plotly
- **Notebook**: Jupyter
- **Orchestrate**: Airflow

**Notes**

- _Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields._
- _The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription._
- _In addition, please note that Transform also has a viewer._
