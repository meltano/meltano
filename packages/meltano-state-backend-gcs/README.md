# Meltano State Backend - Google Cloud Storage

This is the Azure state backend for Meltano.

## Installation

```bash
uvx tool install --with meltano-state-backend-azure meltano
```

## Configuration

```bash
meltano config set state_backend.azure.connection_string <your-azure-connection-string>
meltano config set state_backend.azure.storage_account_url <your-azure-storage-account-url>
```
