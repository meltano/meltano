---
title: Installation
description: Learn how to install Meltano locally with Linux, macOS, Windows, or Docker.
layout: doc
weight: 2
---

Before you can use Meltano, you’ll need to get it installed. We have a [complete installation guide](/guide/installation-guide) that covers all the possibilities, virtual environments and using pipx; this guide will guide you to a fast installation that will work for the tutorial.


## Install Meltano



{% tabs log %}

{% tab log Using Pip %}

Meltano is pip-installable.

Use the following command to check that you have a supported Python version installed:

```bash
python --version
```
Currently Python 3.7, 3.8, 3.9, and 3.10 are supported. Some plugins do not yet support Python 3.10.

<div class="termy">

```console
$ pip install --upgrade pip
Requirement already satisfied.
$ pip install "meltano"
---> 100%
successfully installed meltano
```

</div>

{% endtab %}

{% tab log Using Docker %}
We maintain the `meltano/meltano` Docker image on Docker Hub, which comes with Python and Meltano pre-installed.

To get the latest version of Meltano, pull the latest tag. Images for specific versions of Meltano are tagged v<X.Y.Z>, e.g. v1.55.0. Add a `-python<X.Y>` suffix to the image tag to change the python version, e.g. latest-python3.7.

<div class="termy">
```console
$ docker pull meltano/meltano
latest: Pulling from meltano/meltano
---> 100%
Status: Downloaded newer image for meltano/meltano:latest
docker.io/meltano/meltano:latest

$ docker run meltano/meltano --version
meltano, version 2.7.1
```

</div>

{% endtab %}

{% tab log Using PIPX %}
Meltano is pip-installable.

Use the following command to check that you have a supported Python version installed:

```bash
python --version
```
Currently Python 3.7, 3.8, 3.9, and 3.10 are supported. Some plugins do not yet support Python 3.10.

Pip is a package installer that comes automatically with Python 3+. [pipx](https://pypa.github.io/pipx/) is a wrapper around pip which cleanly installs executable python tools (such as Meltano) into their own virtual environments.

<div class="termy">

```console
$ pipx install "meltano"
---> 100%
successfully installed meltano
```

</div>
{% endtab %}

{% endtabs %}

## More Information
To understand details of the installation, like mounting a docker volume to work long-term with the docker image, view the [detailed installation guide](/guide/installation-guide).
## Next Steps

Once you're set up, head over to the tutorial to learn [how to initialize your first project and start to import data](/getting-started/part1).
<script src="/js/tabs.js"></script>
<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
