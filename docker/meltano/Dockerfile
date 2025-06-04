ARG PYTHON_VERSION="3.9"

FROM python:${PYTHON_VERSION}-slim

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

# Installing the application from a pre-built wheel in the dist directory
RUN --mount=type=bind,source=dist,target=/tmp/meltano-dist \
    pip install --upgrade pip wheel && \
    pip install "meltano[azure,gcs,mssql,postgres,psycopg2,s3] @ file://$(ls /tmp/meltano-dist/meltano-*.whl)"

ENTRYPOINT ["meltano"]
