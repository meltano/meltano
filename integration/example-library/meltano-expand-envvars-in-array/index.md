# Expanding environment variables in elements of an array setting value

This is a simple example of how to expand environment variables in elements of an array setting value.

## Setup

Install the project dependencies:

```shell
meltano install
```

## Run the pipeline

```shell
ANIMAL_GROUP=birds meltano invoke tap-smoke-test
ANIMAL_GROUP=reptiles meltano invoke tap-smoke-test
ANIMAL_GROUP=mammals meltano invoke tap-smoke-test
```
