ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim

ARG MELTANO_VERSION

# Meltano project directory - this is where you should mount your Meltano project
ARG WORKDIR="/project"

ENV PIP_NO_CACHE_DIR=1

RUN mkdir "${WORKDIR}" && \
    apt-get update && \
    apt-get install -y build-essential freetds-bin freetds-dev git libkrb5-dev libssl-dev tdsodbc unixodbc unixodbc-dev && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

WORKDIR "${WORKDIR}"

# Create a virtual environment, and activate it
RUN python -m venv /venv
ENV PATH="/venv/bin:${PATH}"

# Installing the application the same way our users do when using PyPI
RUN pip install --upgrade pip wheel && \
    pip install "meltano[azure,gcs,mssql,postgres,psycopg2,s3]==${MELTANO_VERSION}"

ENTRYPOINT ["meltano"]
