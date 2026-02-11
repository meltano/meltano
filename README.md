<div align="center">
  <picture align="center" with="600">
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/meltano/meltano/assets/5394188/59d36ec9-2e02-45ff-98ea-8b5b1f0fb34f">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/meltano/meltano/assets/5394188/be586327-53b0-43e6-a93e-c7cc2577d9be">
  <img alt="Meltano Logo" src="https://github.com/meltano/meltano/assets/5394188/be586327-53b0-43e6-a93e-c7cc2577d9be" width="600"/>
  </picture>
</div>

<h1 align="center">The declarative code-first data integration engine</h1>
<h3 align="center">Say goodbye to writing, maintaining, and scaling your own API integrations.<br>Unlock 600+ APIs and DBs and realize your wildest data and ML-powered product ideas.</h3>

<div align="center">
<a href="https://meltano.com/demo">
<img alt="Try codespaces" src="https://img.shields.io/static/v1?label=&message=Try live demo with Codespaces&color=02a5a5&style=for-the-badge&logo=github"/>
</a>
</div>

---

<div align="center">
<a href="https://meltano.com/slack">
<img alt="Meltano Community Slack" src="https://img.shields.io/badge/Slack-Join%20the%20Community-blue?logo=slack&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://docs.meltano.com/">
<img alt="Docs" src="https://img.shields.io/website?down_color=red&down_message=offline&label=Docs&up_color=blue&up_message=online&url=https%3A%2F%2Fdocs.meltano.com%2F&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://pypi.org/project/meltano/">
<img alt="Meltano Python Package Version" src="https://img.shields.io/pypi/v/meltano?label=Version&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://github.com/meltano/meltano/graphs/contributors">
<img alt="GitHub contributors" src="https://img.shields.io/github/contributors/meltano/meltano?label=Contributors&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://github.com/meltano/meltano/blob/main/LICENSE">
<img alt="GitHub" src="https://img.shields.io/github/license/meltano/meltano?label=License&labelColor=471E80&color=110B1E"/>
</a>
</div>

<div align="center">
<a href="https://pypi.org/project/meltano/">
<img alt="Supported Python Versions" src="https://img.shields.io/pypi/pyversions/meltano?label=Python&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://pypi.org/project/meltano/">
<img alt="Monthly PyPI Downloads" src="https://img.shields.io/pypi/dm/meltano?label=PyPI%20Downloads&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://hub.docker.com/r/meltano/meltano">
<img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/meltano/meltano?label=Docker%20Pulls&labelColor=471E80&color=110B1E"/>
</a>
</div>

<div align="center">
<a href="https://libraries.io/pypi/meltano/sourcerank">
<img alt="Libraries.io SourceRank" src="https://img.shields.io/librariesio/sourcerank/pypi/meltano?label=SourceRank&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://libraries.io/pypi/meltano">
<img alt="Libraries.io dependency status for latest release" src="https://img.shields.io/librariesio/release/pypi/meltano?label=Dependencies&labelColor=471E80&color=110B1E"/>
</a>
<a href="https://github.com/meltano/meltano/blob/main/CONTRIBUTORS.md">
<img alt="All Contributors" src="https://img.shields.io/github/all-contributors/meltano/meltano?label=All%20Contributors&labelColor=471E80&color=110B1E"/>
</a>
</div>

<div align="center">
<a href="https://github.com/meltano/meltano/actions/workflows/test.yml?query=branch%3Amain">
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/meltano/meltano/test.yml?label=Tests&labelColor=471E80&color=110B1E">
</a>
<a href="https://codecov.io/github/meltano/meltano">
<img alt="Codecov" src="https://img.shields.io/codecov/c/github/meltano/meltano?label=Coverage&labelColor=471E80&color=110B1E">
</a>
</div>

## Integrations

[Meltano Hub](https://hub.meltano.com/) is the single source of truth to find any Meltano plugins as well as [Singer](https://singer.io/) taps and targets. Users are also able to add more plugins to the Hub and have them immediately discoverable and usable within Meltano. The Hub is lovingly curated by Meltano and the wider Meltano community.

## Installation

If you're ready to build your ideal data platform and start running data workflows across multiple tools, start by following the [Installation guide](https://docs.meltano.com/getting-started/installation) to have Meltano up and running in your device.

### Docker Images

Meltano is available as Docker images on [Docker Hub](https://hub.docker.com/r/meltano/meltano):

- **Slim images** (recommended): `meltano/meltano:latest-slim` - optimized size, includes cloud storage support
- **Full images**: `meltano/meltano:latest` - includes all database connectors and build tools

```bash
# Quick start with slim image
docker run --rm meltano/meltano:latest-slim --version

# For projects needing MSSQL/PostgreSQL
docker run --rm meltano/meltano:latest --version
```

See our [Containerization guide](https://docs.meltano.com/guide/containerization) for detailed usage instructions.

## Documentation

Check out the ["Getting Started" guide](https://docs.meltano.com/getting-started) or find the full documentation at [https://docs.meltano.com](https://docs.meltano.com/).

## Contributing

Meltano is a truly open-source project, built for and by its community. We happily welcome and encourage your contributions. Start by browsing through our [issue tracker](https://github.com/meltano/meltano/issues?q=is%3Aopen+is%3Aissue) to add your ideas to the roadmap. If you're still unsure on what to contribute at the moment, you can always check out the list of open issues labeled as "[Accepting Merge Requests](https://github.com/meltano/meltano/issues?q=is%3Aopen+is%3Aissue+label%3A%22accepting+merge+requests%22)".

For more information on how to contribute to Meltano, refer to our [contribution guidelines](https://docs.meltano.com/contribute/).

## Community

We host weekly online events where you can engage with us directly. Check out more information in our [Community](https://meltano.com/community/) page.

If you have any questions, want sneak peeks of features or would just like to say hello and network, join our community of over +2,500 data professionals!

👋 [Join us on Slack!](https://meltano.com/slack)

## Responsible Disclosure Policy

Please refer to the [responsible disclosure policy](https://docs.meltano.com/contribute/responsible-disclosure) on our website.

## License

This code is distributed under the MIT license, see the [LICENSE](https://github.com/meltano/meltano/blob/main/LICENSE) file.
