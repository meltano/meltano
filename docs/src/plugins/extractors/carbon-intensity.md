---
sidebar: auto
metaTitle: Extract Data from Great Britain's Carbon Emissions API
description: Use Meltano to extract raw data from Great Britain's Carbon Emissions API and insert it into Postgres, Snowflake, and more. 
---

# Carbon Intensity

The **Carbon Intensity** extractor pulls data from the Official Carbon Emissions Intensity API for Great Britain, which was developed by the [National Grid](https://www.nationalgrid.com/uk). It is an interesting data source for playing with Meltano's analytical tools before you start connecting your own sources.

## Hosted Accounts

From within your Meltano account, navigate to the *Pipelines* tab in the top navigation and select Extract: [https://meltano.meltanodata.com/pipeline/extract/](https://meltano.meltanodata.com/pipeline/extract/)

![Screenshot of Meltano UI](/images/csv-tutorial/01-csv-extractor-selection.png)

Select "Configure" to install the Extractor. Because it is an open API, no credentials are required and you will be advanced to the next step in setting up your pipeline.

## Self-Hosted Users

### Installation

`tap-carbon-emissions` comes with your Meltano instance, and you can configure it from the UI or the command line.

#### Command Line Insructions 

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-carbon-intensity
```

If you are successful, you should see `Added and installed extractors 'tap-carbon-intensity'` in your terminal.
