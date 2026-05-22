---
title: ChannelML
description: Reference documentation for channel definition model.
sidebar_position: 2
---

Examples and reference documentation for organising your datasets into channels.

Use the channel YAML to group related datasets in your workspace as code.

Our channel files are stored as YAML files, you can read more about the YAML format and its syntax [here](https://yaml.org/).

---

### Example: `analyze/channels/tap-google-analytics/google_analytics.yml`

```yaml
version: channels/v0.1
name: Google Analytics
description: Google Analytics
picture: /assets/images/datasource/tap-google-analytics.svg
```

### Key Information

Path | JSON Type | Description
---- | --------- | -----------
`version` | `string` | The version determines how the CLI handles publishing the channel.
`name` | `string`  | Alias of your channel. Unique to the workspace, used for updating and verify channel updates.
`description` | `string` | Text displayed in Meltano Cloud below the channel icon.
`image` | `string` | An image url or local reference for your channel icon. If left empty, will use the icon of the user who created the channel.

## String Formatting

You may use any of the following string formats:
```yaml
description: My Channel

description: 'My Channel'

description: "My Channel"

description: |-
    My Channel
    Multi-line string, remember to indent
```

---

Further Reading:

- [API Channels](/reference/cloud/api/resources/channels)
