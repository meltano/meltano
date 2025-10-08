ARG PYTHON_VERSION="3.13"

FROM python:${PYTHON_VERSION}-slim

LABEL org.opencontainers.image.source=https://github.com/meltano/meltano
LABEL org.opencontainers.image.description="Meltano: Your DataOps OS. The declarative code-first data integration engine that powers your wildest data and ML-powered product ideas."
LABEL org.opencontainers.image.licenses=MIT

# Meltano project directory - this is where you should mount your Meltano project
ARG WORKDIR="/project"

ENV PIP_NO_CACHE_DIR=1

RUN mkdir "${WORKDIR}" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      freetds-bin \
      freetds-dev \
      git \
      libkrb5-dev \
      libssl-dev \
      tdsodbc \
      unixodbc \
      unixodbc-dev && \
    pip install --no-cache-dir uv && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

WORKDIR "${WORKDIR}"

# Create a virtual environment, and activate it
RUN uv venv /venv
ENV PATH="/venv/bin:${PATH}"

# Installing the application from a pre-built wheel in the dist directory
RUN --mount=type=bind,source=dist,target=/tmp/meltano-dist \
    uv pip install "meltano[azure,gcs,mssql,postgres,s3] @ file://$(ls /tmp/meltano-dist/meltano-*.whl)"

ENTRYPOINT ["meltano"]
