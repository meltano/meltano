---
title: Inline Data Mapping
description: Alter records and streams on the fly.
layout: doc
sidebar_position: 5
---

Meltano gives you the flexibility to alter data passing through your EL pipelines to do precisely what you need for your use case.
Although commonly users want to replicate their data in the most raw format, using [ELT vs ETL](https://meltano.com/blog/the-benefits-of-elt-vs-etl-what-you-need-to-know/), there are many use cases that require minor alterations to data on the fly.
This is where mappers, also referred to as inline stream maps, shine!

# Features

The mapper features can be viewed in 2 categories: stream level or property (record) level.
Stream level features allow you to modify the stream itself, whereas the property level features allow you to modify contents of the stream.

## Stream Level

- Aliasing: streams can be aliased to provide custom naming downstream.
- Filtering: stream records can be filtered based on any user-defined logic.
- Duplication: streams can be split or duplicated and then sent as multiple distinct streams to the downstream target.

## Property (Column) Level

- Aliasing: properties can be renamed in the resulting stream e.g. altering a column name from `id` -> `customer_id`
- Transformations: properties can be transformed inline e.g. upper casing, casting types, etc.
- Exclusions: properties can be removed from the resulting stream.
- Additions: new properties can be created based on inline user-defined expressions.
- Flatten nested properties: separates large complex properties into multiple distinct fields.

## Out of Scope Features

- Mappers do not support aggregation. To aggregate data, first land the data in your destination and then apply aggregations using a [transformation plugin](/guide/transformation) like dbt.
- Mappers do not support joins between streams. To join data, first land the data and then perform joins using a transformation tool like dbt.
- Mappers do not support external API lookups. To add external API lookups, you can either (a) land all your data and then joins using a [transformation plugin](/guide/transformation) like dbt, or (b) create a custom mapper plugin with inline lookup logic.

# Use Cases

There are lots of use cases for mappers and part of their benefit is allowing you to add custom behavior into your pipelines even when using out of the box connectors.
Here are a few examples of common use cases for mappers.

## PII hashing or removal

Some users have strict requirements to not store any raw PII data in their destination system.
In this case you can use mappers to either hash the PII data on the fly so it arrives in your destination but not in plain text, or you can simply remove it.
If you need to remove PII you can consider using selection criteria to avoid replicating it in the first place but mappers give you more precision if needed.

## Altering Tap Behavior

Sometimes users will install a tap from MeltanoHub and realize that its providing the data they want but maybe not in a custom format they need.
There are at least 2 options:

1. Fork the tap, make the code changes you need for your use case, and maintain that new variant moving forward
2. Use mappers to alter the output of the generic tap to fit your custom use case without editing the tap itself

Using mappers in option 2 allows you to get the behavior that you want without the burden of making code changes and maintaining a custom variant moving forward.

## Renaming Streams

Mappers let you make stream level alterations like renaming, duplicating, or splitting a stream.
This can be used to enforce consistent naming conventions for tables in your warehouse or duplicating a stream to add mapper alterations while also preserving the original stream.
Another example is for reverse ETL use cases where the target usually expects the data to arrive in streams and fields named in a particular way, you can achieve this using mappers.

## Other Uses

- Modify primary keys
- Splitting streams
- Filtering record based on conditions
- Type casting
- Casing updates
- Coalescing values

# Running Mappers

There are two ways to use mapper functionality within Meltano.
You can install a standalone mapper plugin that runs between a tap and a target i.e. `meltano run tap-csv <MAPPER> target-jsonl` or if either your tap or target is based on the Meltano SDK then you can configure the `stream_map_config` settings in the plugin configuration, also referred to as inline stream maps.

## SDK Stream Maps

If either your tap or your target is built on the Meltano SDK then it automatically has the mapper features, or also referred to as inline stream maps, built in.
This is the easiest way to get mapper functionality into your pipeline by avoiding some of the limitations of standalone mappers (only works with `meltano run`, requires installing another plugin, etc.).
The limitation is that the mapper functionality is baked into the SDK so if you ever need to make customizations its a bit less flexible relative to standalone mappers where you can create your own forks.

A few example configurations using inline stream maps are:

#### Example

This example shows the SDK based meltanolabs variant of tap-github configured to lowercase all repo names in the issues stream.

```yaml
  - name: tap-github
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-github.git
    config:
      stream_maps:
        issues:
          repo: record['repo'].lower()
```

For more details and examples refer to the [SDK documentation](https://sdk.meltano.com/en/latest/stream_maps.html).

## Standalone Mapper Plugins

The other way of getting mapper functionality is to use a standalone mapper plugin that is inserted between your tap and target to do the translation `meltano run tap-csv <MAPPER> target-jsonl`.
These can be used even when your your tap and/or target are not SDK based.

The limitation with this approach is that currently you can only run these using the `meltano run` command and not using `meltano elt` or `meltano invoke`.
The advantage relative to the SDK inline stream maps is that you can fork the mapper plugin or build your own to do whatever you need.

The two most common mapper plugins are:

- [meltano-map-transform](https://github.com/MeltanoLabs/meltano-map-transform)
- [pipelinewise-transform-field](https://github.com/transferwise/pipelinewise-transform-field)

These can be added like any other plugin:

```bash
meltano discover mappers
meltano add mapper <mapper name>

# Example
meltano add mapper meltano-map-transformer
```

#### Example

An example taken from the [meltano-map-transformer](https://github.com/MeltanoLabs/meltano-map-transform/tree/main/examples) repository shows the mapper altering casing of the data.
Given this input CSV and mapper configurations:

```csv
id,first_name,last_name,email,ip_address
1,Ethe,Book,ebook0@twitter.com,67.61.243.220
```

```yaml
plugins
  mapper:
    - name: meltano-map-transformer
    variant: meltano
    pip_url: git+https://github.com/MeltanoLabs/meltano-map-transform.git
    mappings:
    - name: lower
      config:
        stream_maps:
          customers:
            __alias__: customers_v5
            first_name: first_name.lower() # three different ways of accessing the variable
            last_name: record['last_name'].lower()
            email:  _['email'].upper()
            count_t: str(last_name.count("t")) # need to cast to str because it could be NULL!
            ip_address: __NULL__
```

After running `meltano run tap-csv lower target-sqlite` the result would be:

| count_t | email              | first_name | id  | last_name | \_\_loaded_at              |
| ------- | ------------------ | ---------- | --- | --------- | -------------------------- |
| 0       | EBOOK0@TWITTER.COM | ethe       | 1   | book      | 2023-03-17 16:57:19.095880 |

To see more examples check out the [plugin repo](https://github.com/MeltanoLabs/meltano-map-transform/tree/main/examples).

## FAQs

### Can I used standalone mapper plugins with the `meltano elt` command?

No, currently only `meltano run` support standalone mapper plugins.

### Can I use mapping features with the BATCH message type?

No, BATCH message type does not currently support mapping functionality.
Follow along with [this discussion](https://github.com/meltano/meltano/discussions/6639#discussioncomment-3417860) where we talk about how stream maps could support BATCH messages.

### When would I use standalone mapper plugins vs SDK based stream maps?

It's mostly preference but here are some trade offs to consider:

- Mapper plugins can only be run using `meltano run`
- Mappers work for SDK and non-SDK connectors. If your pipeline uses 2 non-SDK connectors this is your best option.
- SDK stream maps are part of the SDK which inherently makes them more difficult to change. If you need custom functionality then forking a mapper plugin and customizing it is you best option. Although if your behavior is generically useful, please open an issue in the [SDK repo](https://github.com/meltano/sdk) to get it added!
- SDK stream maps avoid having to install an additional plugin into your project.
- Mapper plugins alter data after its been extracted whereas SDK based stream maps on the tap side could alter the extraction behavior.
  Depending on your use case, for example deleting streams, it might be slightly more efficient to do it in the tap and avoid extracting unneeded data.

### Do both my tap and target need to support SDK based stream maps?

No, you only need one of your plugins to be SDK based in order to get this functionality.
