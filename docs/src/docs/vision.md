# Meltano Vision

_This document represent my vision for Meltano as an open-source project, a collaboration tool and a framework for data projects._

## Our mantra

> A single workflow for the entire data life cycle.
> Meltano leverages best practices from software development such as version control, continuous integration and deployment, and a > powerful command line interface so you can focus on your data.

As a convention over configuration framework, we want to graps the general patterns present in data projects and define a workflow that includes the most of it.

### The Meltano Project

A Meltano project should define the specifics of your project.

  - Data sources, and their configurations (extractors)
  - Warehouses, and their configurations  (loaders)
  - What are the defined manipulations on the data (transforms)
  - How do you expose the data to the end-users (models)

This is the basis of a Meltano project, it defines what will be available (ELT) and how it is exposed back (M).

#### Data Project as Code

The crux of the Meltano project is the fact it is treated as any software project: code.
This enables a Meltano project to be:

  - Portable: a project should run on all supported platforms
  - Reproductible: a project should run in isolation (development vs. production), for instance on a developer's device
  - Collaborative: a project should support collaborative workflows as VCS enable it

#### First-class deployment

Deployment is an integral part of the DevOps pipeline, typically using CI/CD pipelines to achieve fast deployment cycles.

Meltano projects supports CI/CD deployment such as:

_TODO: add CI/CD schema_

#### Compile time vs. Runtime

Meltano concepts can be split into two categories, compile time and runtime:

Compile time:
  - Plugin declarations
  - Model definitions
  - Custom transforms
  - Custom DAGs

Runtime:
  - Orchestration schedules
  - Plugin configuration
  - Secrets

#### Meltano UI

The Meltano UI serves as an entry point to **build**, **manage** and **consult** your Meltano project:

  - Build: provides tools to manage the installed components in your Meltano project
  - Manage: provides tools to define the runtime configuration of your Meltano project
  - Consult: provides tools to explore, analyze and interact with the data

In a production environment, the `Build` section should be disabled to make sure the Meltano project is not altered between deploys.

#### Collaboration in Meltano

##### Internal

Because the Meltano project is defined as code, standard DevOps best-practices can be used, enabling better collaboration inside a Meltano project's team.

Typical use-case, a developer add a new model:

_The developer runs the Meltano project locally_

  1. Fetch some data from the data source. It can be a small subset.
  1. Create the new model, looking at the Meltano compiler for errors
  1. When the model is done, consult it in the Meltano UI
  1. When satisfied with the model, commit and push to the repository
  1. Automated tests should run on the model, these tests could have greater coverage than the initial data set the developer uses
  1. After peer-review, the change is accepted and will be published via the next deploy

##### External (cross-project)

Because of the component nature of Meltano, users will be able to provide definitions as building blocks for other Meltano project to consume. Here are a couple examples of how Meltano enable cross-project collaboration:

  - A company publish transforms & models for a data source they use, any other Meltano project can use them
  - A company publish an extractor (singer tap), any other Meltano project can use it
  - A company publish a loader (singer target), any other Meltano project can use it
  - You find an interesting dashboard on the web, you can look at the source to see how it is defined (replicate)
