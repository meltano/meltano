# Meltano State Backend - AWS S3

This is the S3 state backend for Meltano.

## Installation

```bash
uvx tool install --with meltano-state-backend-s3 meltano
```

## Configuration

```bash
meltano config set state_backend.s3.aws_access_key_id <your-aws-access-key-id>
meltano config set state_backend.s3.aws_secret_access_key <your-aws-secret-access-key>
meltano config set state_backend.s3.endpoint_url <your-s3-endpoint-url>
```
