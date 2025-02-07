# Expanding environment variables in elements of an array setting value

This is a simple example of how to expand environment variables in elements of an array setting value.

## Setup

Install the project dependencies:

```shell
meltano install
```

## Run the pipeline

```shell
ANIMAL_GROUP=birds meltano run tap-smoke-test target-csv
ANIMAL_GROUP=reptiles meltano run tap-smoke-test target-csv
ANIMAL_GROUP=mammals meltano run tap-smoke-test target-csv
```
