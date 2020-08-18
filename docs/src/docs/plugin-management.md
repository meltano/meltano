---
metaTitle: Managing your Meltano plugins
description: Learn how to add extractors and loaders to your project
---

# Plugin management

## Adding extractors and loaders to your project

Like all types of plugins, extractors and loaders can be added to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add).

Plugins that are already [known to Meltano](/docs/contributor-guide.html#known-plugins) can be added by simply specifying their `type` and `name`, while adding a plugin that Meltano isn't familiar with yet requires adding the `--custom` flag.

To find out what plugins are already known to Meltano and supported out of the box, you can use [`meltano discover`](/docs/command-line-interface.html#discover), with an optional pluralized `plugin type` argument.
You can also check out the lists of supported [extractors](/plugins/extractors/) and [loaders](/plugins/loaders/) on this website.

If the Singer tap or target you'd like to use with Meltano doesn't show up in any of these places, you're going to want to [add a custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins).

```bash
# List extractors and loaders known to Meltano
meltano discover extractors
meltano discover loaders

# Add a known extractor or loader by name
meltano add extractor tap-salesforce
meltano add loader target-snowflake

# Add an unknown (custom) extractor or loader
meltano add --custom extractor tap-covid-19
```
