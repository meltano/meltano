---
title: Plugins
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
hidden: true
---

## Discoverable plugins

[Discoverable plugins](/concepts/plugins#discoverable-plugins) that are supported out of the box are available in [Meltano Hub](https://hub.meltano.com).

### Making a custom plugin discoverable

If you've added a [custom plugin](/concepts/plugins#custom-plugins) (or [variant](/concepts/plugins#variants)) to your project that could be discoverable and supported out of the box for new users, please [contribute](https://github.com/meltano/hub/issues/new) its description to Meltano Hub to save the next user the hassle of setting up the custom plugin.
GitHub makes it easy to contribute changes without requiring you to leave your browser.

Discoverable plugin definitions in Meltano Hub have the a very similar format as [custom plugin definition](/concepts/project#custom-plugin-definitions) in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file), so a copy-paste is usually sufficient.

The format and further requirements are laid out in more detail in the [Meltano Hub plugin definition syntax](/reference/plugin-definition-syntax) document.

### Adopting a plugin

When the maintainer of the default [variant](/concepts/plugins#variants) of a discoverable plugin becomes unresponsive to issues and contributions filed by the community,
that plugin is considered up for adoption, which means that we are looking for a different variant of the plugin with a more engaged maintainer to become the new default.

This new variant can either be a fork of the original default variant, or an alternative implementation for the same source or destination, as long as it is actively maintained.

If you maintain or are aware of such a variant,
please add it to your Meltano project as a [custom plugin](/concepts/plugins#custom-plugins) and [make it discoverable](#making-a-custom-plugin-discoverable),
or [file an issue](https://github.com/meltano/meltano/issues/new) so that the Meltano core team can assist you.

As a plugin's primary maintainer, you do not have to spend a lot of time improving the plugin yourself.
In fact, attracting more users and getting the community involved is likely to recude your personal maintenance burden,
since you'll receive contributions with bug fixes and new features that you will only be expected to review, not build yourself.

## Plugin Development

### <a name="taps-targets-development"></a>Taps & Targets Development

Watch ["How taps are built"](https://www.youtube.com/watch?v=aImidnW8nsU) for an explanation of how Singer taps (which form the basis for Meltano extractors) work, and what goes into building new ones or verifying and modifying existing ones for various types of APIs.

Then watch ["How transforms are built"](https://www.youtube.com/watch?v=QRaCSKQC_74) for an explanation of how DBT transforms work, and what goes into building new ones for new data sources.

#### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

##### How to test a tap?

We qualify taps with the capabilities it supports:

- properties: the tap uses the old `--properties` format for the catalog
- catalog: the tap uses the new `--catalog` format for the catalog
- discover: the tap supports catalog extraction
- state: the tap supports incremental extraction

###### Properties/Catalog

You should look at the tap's documentation to see which one is supported.

###### Discover

Try to run the tap with the `--discover` switch, which should output a catalog on STDOUT.

###### State

1. Try to run the tap connect and extract data first, watching for `STATE` messages.
1. Do two ELT run with `target-postgres`, then validate that:
   1. All the tables in the schema created have a PRIMARY KEY constraint. (this is important for incremental updates)
   1. There is no duplicates after multiple extractions

##### Troubleshooting

###### Tables are lacking primary keys

This might be a configuration issue with the catalog file that is sent to the tap. Take a look at the tap's documentation and look for custom metadata on the catalog.

#### For taps/targets we create

1. For tap and target development please use the [Meltano Singer SDK](https://sdk.meltano.com/en/latest/).
1. Use a separate repo (meltano/target|tap-x) in GitHub
   e.g. Snowflake: https://github.com/meltanolabs/target-snowflake
1. Publish PyPI packages of these package (not for now)
