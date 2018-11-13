# Meltano Guide and API Reference

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Hub Account](https://hub.docker.com/)

## Building the Docs

1. Navigate to project root directory in terminal
1. Run `make docs_image`
1. Run `make docs_shell`
    - You will be launched into a bash shell with everything you need to build the docs.
1. Run `make html`
    - This will generate all the documentation from the Python Documentation Generator: [Sphinx](http://www.sphinx-doc.org/en/master/).

You can also just run `make docs/build` and it will do everything for you.

If you want to replicate the build environment outside docker you can probably
get away with following
[this guide](https://docs.readthedocs.io/en/latest/intro/getting-started-with-sphinx.html).

## Previewing the docs

You may use the `make docs/serve` command to have a local preview of the docs at http://localhost:8080
