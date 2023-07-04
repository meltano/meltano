---
title: Installation
description: Learn how to install Meltano locally with Linux, macOS, Windows, or Docker.
layout: doc
weight: 2
---

Before you can use Meltano, you’ll need to get it installed. We have a [complete installation guide](/guide/installation-guide) that covers all the possibilities, virtual environments and using pipx; this guide will guide you to a fast installation that will work for the tutorial.

## Install Meltano

Use the following command to check that you have a supported Python version installed:

```bash
python --version
```

Meltano supports all versions of Python that have not yet reached their end-of-life date. Refer to [the official Python documentation for when versions of Python will reach end-of-life](https://devguide.python.org/versions/).

<div class="notification is-warning">
  <p>Not all plugins support the latest versions of Python.</p>
</div>

{% tabs log %}

{% tab log Using pipx %}

Since Meltano is an application, it should always be installed into a clean virtual environment without any other packages installed alongside it.

To simplify installing Meltano into a clean virtual environment, [`pipx`](https://pypa.github.io/pipx/) can be used to install Meltano instead of `pip`. `pip` is a package installer that comes automatically with Python. `pipx` is a wrapper around pip which cleanly installs executable Python applications (such as Meltano) into their own virtual environments.

<div class="termy">

```console
$ pipx install "meltano"
---> 100%
successfully installed meltano
```

</div>

{% endtab %}

{% tab log Using Docker %}

We maintain [the `meltano/meltano` Docker image on Docker Hub](https://hub.docker.com/r/meltano/meltano/tags), which comes with Python and Meltano pre-installed.

To get the latest version of Meltano, pull the latest tag. Images for specific versions of Meltano are tagged `v<major>.<minor>.<patch>`, e.g. `v2.19.0`. Add a `-python3.X` suffix to the image tag to change the python version, e.g. `latest-python3.9`. To get the latest minor or patch version, omit that value from the version number, e.g. `v2` for the latest Meltano `v2.*.*` image, or `v2.19` for the latest Meltano `v2.19.*` image

<div class="termy">
```console
$ docker pull meltano/meltano
latest: Pulling from meltano/meltano
---> 100%
Status: Downloaded newer image for meltano/meltano:latest
docker.io/meltano/meltano:latest

$ docker run meltano/meltano --version
meltano, version 2.19.0

````

</div>

{% endtab %}

{% tab log Using pip %}

Meltano provides a Python package that can be installed using `pip`.

<div class="notification is-warning">
  <p>To avoid dependency conflicts, please ensure Meltano is installed into a clean Python virtual environment.</p>
</div>

<div class="termy">

```console
$ pip install --upgrade pip
Requirement already satisfied.
$ pip install "meltano"
---> 100%
successfully installed meltano
````

</div>

{% endtab %}

{% endtabs %}

## More Information

To understand details of the installation, like mounting a docker volume to work long-term with the docker image, view the [detailed installation guide](/guide/installation-guide).

## Next Steps

Once you're set up, head over to the tutorial to learn [how to initialize your first project and start to import data](/getting-started/part1).

<script src="/js/tabs.js"></script>
<script src="/util/termynal.js"></script>
<script src="/util/termy_custom.js"></script>
