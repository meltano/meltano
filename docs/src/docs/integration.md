---
metaTitle: Data integration using Meltano
description: Learn how to use Meltano to select specific entities and attributes for extraction
---

# Data Integration (EL)

## Selecting entities and attributes for extraction

Extractors are often capable of extracting many more entities and attributes than your use case may require.
To save on bandwidth and storage, it's usually a good idea to instruct your extractor to only select those entities and attributes you actually plan on using.

With stock Singer taps, entity selection (and specification of other [metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)) involves a few steps. First, you run a tap in
[discovery mode](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md)
to generate a `catalog.json` file describing all available entities and attributes.
Then, you edit this file and add `"selected": true` (and any other metadata) to the `metadata` objects for all of the desired entities and attributes.
Finally, you pass this file to the tap using the `--catalog` flag when you run it in [sync mode](https://github.com/singer-io/getting-started/blob/master/docs/SYNC_MODE.md).
Because these catalog files can be very large and can get outdated as data sources evolve, this process can be tedious and error-prone.

Meltano makes it easy to select specific entities and attributes for inclusion or exclusion using [`meltano select`](/docs/command-line-interface.html#select),
which lets you specify inclusion and exclusion rules using [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like patterns with wildcards (`*`, `?`) and character groups (`[abc]`, `[!abc]`).

Additional [Singer stream and property metadata](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#metadata)
(like `replication-method` and `replication-key`) can be specified like
any other [plugin configuration](/docs/configuration.html), using a special
[`_metadata` setting](/docs/command-line-interface.html#extractor-extra-metadata) with
[nested properties](/docs/command-line-interface.html#nested-properties)
`_metadata.<entity>.<key>` and `_metadata.<entity>.<attribute>.<key>`.

Similarly, a special [`_schema` setting](/docs/command-line-interface.html#extractor-extra-schema)
is available that lets you easily override
[Singer stream schema](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#schemas) descriptions.
Like selection rules, these metadata and schema rules allow for [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like
patterns in the entity and attribute identifiers.

Whenever an extractor is run using [`meltano elt`](/docs/command-line-interface.html#elt)
or [`meltano invoke`](/docs/command-line-interface.html#invoke), Meltano will
generate the desired catalog on the fly by running the tap in
discovery mode and applying the selection, metadata, and schema rules to the resulting catalog file
before passing it to the tap in sync mode.

Note that exclusion takes precedence over inclusion: if an entity or attribute is matched by an exclusion pattern, there is no way to get it back using an inclusion pattern unless the exclusion pattern is manually removed from your project's `meltano.yml` file first.

If no rules are defined using `meltano select`, Meltano will fall back on catch-all rule `*.*` so that all entities and attributes are selected.
