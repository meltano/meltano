---
sidebar: auto
metaTitle: Extract tabular data from CSVs and Excel spreadsheet files on Cloud or local storage 
description: Use Meltano to extract raw data from multiple CSVs and/or Excel spreadsheets (compressed or not) directly from localhost, S3, GCS, Azure Blob Storage, WebHDFS, SFTP, etc... 
---

# Spreadsheets Anywhere

The [Spreadsheets Anywhere](https://github.com/ets/tap-spreadsheets-anywhere) extractor pulls raw data from files (CSVs or Excel spreadsheets) accessible through popular "Cloud transports" such as:

- S3
- SSH, SCP and SFTP
- HTTP, HTTPS (read-only)
- WebHDFS
- GCS
- Azure Blob Storage

This tap also supports pulling from local directories and will automatically decompress gzip and bzip2 files where
supported.  Multiple individual files with the same schema can be configured & ingested into the same "Table" for processing.

## Info
Please reference the [project repository](https://github.com/ets/tap-spreadsheets-anywhere) for detailed configuration instructions.

## Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-spreadsheets-anywhere
```

