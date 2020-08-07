---
sidebar: auto
metaTitle: Load Data into a JSONL files with Meltano
description: Use Meltano to load data from numerous sources and insert it into a JSONL file.
---

# JSON Lines (JSONL)

[JSON Lines](http://jsonlines.org/) is a convenient format for storing structured data that may be processed one record at a time. It works well with unix-style text processing tools and shell pipelines.

## Info

- **Data Warehouse**: JSONL Files
- **Repository**: <https://github.com/andyh1203/target-jsonl>

## Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```shell
meltano add loader target-jsonl
```

If you are successful, you should see `Added and installed loaders 'target-jsonl'` in your terminal.
