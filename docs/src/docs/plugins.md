---
sidebarDepth: 2
---

# Available Plugins

## Extractors

Extractors are defined as the component that pulls data out of a data source, using the best integration for extracting bulk data.
Currently, Meltano supports [Singer.io](https://singer.io) taps as extractors.

### tap-zuora

<table>
  <tr>
    <th>Data Source</th>
    <td><a target="_blank" href="https://www.zuora.com/">https://www.zuora.com</a></td>
  </tr>
  <tr>
    <th>Repository</th>
    <td><a target="_blank" href="https://github.com/singer-io/tap-zuora">https://github.com/singerio/tap-zuora</a></td>
  </tr>
</table>

#### Default configuration

**.env**
```bash
ZUORA_USERNAME
ZUORA_PASSWORD
ZUORA_API_TOKEN   # preferred to ZUORA_PASSWORD
ZUORA_API_TYPE    # specifically 'REST' or 'AQuA'
ZUORA_PARTNER_ID  # optional, only for the 'AQuA` API type
ZUORA_START_DATE
ZUORA_SANDBOX     # specifically 'true' or 'false'
```
