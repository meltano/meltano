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

This can be customized to use another public mirror, a private mirror (e.g. `your-company/meltano:latest`), a specific version of Meltano (e.g. `meltano/meltano:v3.5-python3.12`), or Python 3.11 or 3.12 (e.g. `meltano/meltano:latest-python3.12` or `meltano/meltano:v3.5-python3.12`) by modifying the `Dockerfile` or overriding the `MELTANO_IMAGE` [`--build-arg`](https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg). We currently publish release images to [Docker Hub](https://hub.docker.com/r/meltano/meltano). Using an alternative public mirror, or creating a private one, can avoid issues during your Docker build stage relating to registry rate limits.

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
