# Meltano Guide and API Reference

## Building the Docs

Run `make docs_image`

Run `make docs_shell`. you will be launched into a
bash shell with everything you need to build the docs.

Then run `make html`

You can also just run `make docs/build` and it will do everything for you.

If you want to replicate the build environment outside docker you can probably
get away with following
[this guide](https://docs.readthedocs.io/en/latest/intro/getting-started-with-sphinx.html).