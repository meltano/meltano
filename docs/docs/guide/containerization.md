---
title: Run in Containers
description: Learn how to greatly simplify the deployment process (and prevent issues caused by inconsistencies between environments!) by wrapping your Meltano project up into a project-specific Docker container image.
layout: doc
sidebar_position: 8
---

Once you've [set up a Meltano project](/concepts/project) and
[run some pipelines](/guide/integration) on your local machine,
it'll be time to repeat this trick in production!

The [Deployment in Production guide](/guide/production) will walk you through getting
Meltano, your project, and all of its plugins onto a new environment one-by-one, among other things, but
you can greatly simplify this process (and prevent issues caused by inconsistencies between environments!)
by wrapping them all up into a project-specific
[Docker container image](https://www.docker.com/resources/what-container):
"a lightweight, standalone, executable package of software that includes everything
needed to run an application: code, runtime, system tools, system libraries and settings."

This image can then be used on any environment running [Docker](https://www.docker.com/)
(or a compatible tool like [Kubernetes](https://kubernetes.io/)) to directly
[run](https://docs.docker.com/engine/reference/commandline/run/)
[`meltano` commands](/reference/command-line-interface)
in the context of your project, without needing to separately manage the installation of
Meltano, your project's plugins, or any of their dependencies.

If you're storing your Meltano project in version control on a
platform like [GitLab](https://about.gitlab.com) or [GitHub](https://github.com),
you can set up a CI/CD pipeline to run every time a change is made to your project,
which can automatically [build](https://docs.docker.com/engine/reference/commandline/build/)
a new version of the image and [push](https://docs.docker.com/engine/reference/commandline/push/)
it to a container registry.
The image can then be [pulled](https://docs.docker.com/engine/reference/commandline/pull/)
from that registry onto any local or cloud environment on which you'd like to run your project's pipelines.

If you'd like to containerize your Meltano project, you can easily add the
appropriate `Dockerfile` and `.dockerignore` files to your project by adding the
[`docker` file bundle](https://github.com/meltano/files-docker):

```bash
# For these examples to work, ensure that
# Docker has been installed
docker --version

# Add Docker files to your project
meltano add files files-docker

# Build Docker image containing
# Meltano, your project, and all of its plugins
docker build --tag meltano-demo-project:dev .
```

Files added to your project include a `Dockerfile` inheriting `FROM` the public [`meltano/meltano:latest`](https://hub.docker.com/r/meltano/meltano/tags) image available on [Docker Hub](https://hub.docker.com).

## Image Variants

Meltano provides two types of Docker images to suit different use cases:

### Full Images (Default)
- **Tags**: `latest`, `v3.9.1`, `latest-python3.11`, etc.
- **Includes**: All database connectors (PostgreSQL, MSSQL), build tools, and system dependencies
- **Use when**: You need MSSQL or PostgreSQL connectivity, or require plugins with complex system dependencies

### Slim Images (Recommended)
- **Tags**: `latest-slim`, `v3.9.1-slim`, `latest-python3.11-slim`, etc.
- **Includes**: Azure, GCS, and S3 connectors with minimal dependencies
- **Excludes**: MSSQL/PostgreSQL connectors, build tools (gcc, make, etc.)
- **Use when**: You primarily use cloud storage backends and want faster downloads and smaller deployments

### Choosing the Right Image

**Use slim images if you:**
- Primarily use cloud storage (S3, GCS, Azure Blob Storage)
- Want faster container startup and deployment times
- Don't require MSSQL or PostgreSQL database connectivity
- Are using plugins that don't need compilation or complex system dependencies

**Use full images if you:**
- Need MSSQL or PostgreSQL database connectivity
- Use plugins requiring build tools or complex system dependencies
- Need the complete set of database connectors and system tools

## Customizing the Base Image

You can customize the base image by modifying the `Dockerfile` or overriding the `MELTANO_IMAGE` [`--build-arg`](https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg):

- **Public mirror**: `your-company/meltano:latest`
- **Specific version**: `meltano/meltano:v3.9.1` or `meltano/meltano:v3.9.1-slim`
- **Python version**: `meltano/meltano:latest-python3.12` or `meltano/meltano:latest-python3.12-slim`

### Examples

```bash
# Use slim image (recommended for most use cases)
docker build --build-arg MELTANO_IMAGE=meltano/meltano:latest-slim --tag my-project:dev .

# Use specific version with Python 3.11
docker build --build-arg MELTANO_IMAGE=meltano/meltano:v3.9.1-python3.11-slim --tag my-project:dev .

# Use full image for MSSQL/PostgreSQL support
docker build --build-arg MELTANO_IMAGE=meltano/meltano:latest --tag my-project:dev .
```

We currently publish release images to [Docker Hub](https://hub.docker.com/r/meltano/meltano). Using an alternative public mirror, or creating a private one, can avoid issues during your Docker build stage relating to registry rate limits.

The built image's [entrypoint](https://docs.docker.com/engine/reference/builder/#entrypoint)
will be [the `meltano` command](/reference/command-line-interface),
meaning that you can provide `meltano` subcommands and arguments like `run ...` and `invoke airflow ...` directly to
[`docker run <image-name> ...`](https://docs.docker.com/engine/reference/commandline/run/)
as trailing arguments:

```bash
# View Meltano version
docker run meltano-demo-project:dev --version

# Run gitlab-to-jsonl pipeline with
# mounted volume to exfiltrate target-jsonl output
docker run \
  --volume $(pwd)/output:/project/output \
  meltano-demo-project:dev \
  run tap-gitlab target-jsonl
```

## Docker Compose

If you'd like to use [Docker Compose](https://docs.docker.com/compose/) to experiment with
a [production-grade](/guide/production) setup of your containerized project,
you can add the appropriate `docker-compose.prod.yml` file to your project by adding the
[`docker-compose` file bundle](https://github.com/meltano/files-docker-compose):

```bash
# For these examples to work, ensure that
# Docker Compose has been installed
docker compose --version

# Add Docker Compose files to your project
meltano add files files-docker-compose

# Start the `meltano-system-db` service in the background
docker compose -f docker-compose.prod.yml up -d
```

For more details and instructions, refer to [README](https://github.com/meltano/files-docker-compose/blob/main/bundle/README.md) contained in the file bundle.

## GitLab CI/CD

If you'd like to use [GitLab CI/CD](https://docs.gitlab.com/ee/ci/) to continuously
build your Meltano project's Docker image and push it to GitLab's built-in
[Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/),
you can add the appropriate `.gitlab-ci.yml` and `.gitlab/ci/docker.gitlab-ci.yml`
files to your project by adding the
[`gitlab-ci` file bundle](https://gitlab.com/meltano/files-gitlab-ci):

```bash
# For these examples to work, ensure that
# you have an account on GitLab.com or
# a self-hosted GitLab instance with
# GitLab CI/CD and Container Registry enabled

# Add GitLab CI/CD files to your project
meltano add files files-gitlab-ci

# Initialize Git repository, if you haven't already
git init

# Add and commit all files
git add -A
git commit -m "Set up Meltano project with Docker and GitLab CI"

# Push to GitLab, which will automatically create
# a new private project at the specified path
NAMESPACE="<your-gitlab-username-or-group>"
git push git@gitlab.com:$NAMESPACE/meltano-demo-project.git master
```

GitLab CI/CD will now start building your Meltano project's dedicated Docker image,
which will be available at `registry.gitlab.com/$NAMESPACE/meltano-demo-project:latest`
once the CI/CD pipeline completes.
