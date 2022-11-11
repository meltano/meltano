# Using S3 as a state backend

```bash @mdsh
mdsh-lang-python() { python; }
```

To begin, download or copy the [meltano.yml](/docs/example-library/meltano-s3/meltano.yml) to an empty directory and run:

```shell
meltano install
```
## Set up Minioadmin

[MinIO](https://min.io) provides S3-compatible storage that can be run in a container.
We'll set up a minio [Docker](https://www.docker.com) container to use as our state backend.

```shell
docker run -d  --name minio -p 9001:9001 -p 9000:9000 quay.io/minio/minio server /data --console-address ":9001"
```

Now we need to create a bucket to store state in.
Open up the Minio Admin console at `http://localhost:9001` in a web browser and log in using the default Minio credentials: `minioadmin` for both username and password.

Then create a bucket with the name `meltano`

Alternatively you could create the bucket using [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html):

```python
from boto3.session import Session

session = Session(aws_access_key_id="minioadmin", aws_secret_access_key="minioadmin")

client = session.client("s3", endpoint_url="http://127.0.0.1:9000")

client.create_bucket(Bucket="meltano")
```


## Configure meltano to use S3 for state.

```shell
meltano config meltano set state_backend.uri "s3://meltano/state"

meltano config meltano set state_backend.s3.aws_access_key_id "minioadmin"
meltano config meltano set state_backend.s3.aws_secret_access_key "minioadmin"
meltano config meltano set state_backend.s3.endpoint_url "http://127.0.0.1:9000"
```

## Configure the tap and target

```shell
meltano config tap-gitlab set start_date 2022-11-01T00:00:01Z
meltano config target-jsonl set do_timestamp_file false
```

## Run a job

```shell
meltano run tap-gitlab target-jsonl
```

## Check state output

```shell
meltano state get dev:tap-gitlab-to-target-jsonl
```
