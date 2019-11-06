---
sidebar: auto
metaTitle: Load Data into a CSV with Meltano
description: Use Meltano to load data from numerous sources and insert it into a CSV for easy analysis.
---

# Comma Separated Values (CSV)

Comma Separated Values, better known as spreadsheets, are the swiss army knife of data analysis. Loading data into this format will create .CSV files that can be used with many other tools that are able to import/export this file type.

## Info

- **Data Warehouse**: CSV Files
- **Repository**: [https://gitlab.com/meltano/target-csv](https://gitlab.com/meltano/target-csv)

## Installing from the Meltano UI

From the Meltano UI, you can [select this Loader in Step 3 of your pipeline configuration](http://localhost:5000/pipelines/loaders).

### Configuration

Once the loader has installed, a modal will appear with options for selecting the Delimiter and Quotechar you would like Meltano to use when loads your data into CSV format. The most commonly used options are selected by default.

## Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add loader target-csv
```

If you are successful, you should see `Added and installed loaders 'target-csv'` in your terminal.

### CLI Configuration

If you want to customize your delimited or quote character, open `meltano.yml` for your desired project and update the configuration there.

```yaml{1-3}
- config:
    delimiter": "\t"
    quotechar": "'"
  name: target-csv
  pip_url: git+https://gitlab.com/meltano/target-csv.git
```
