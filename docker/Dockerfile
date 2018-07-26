FROM python:3.6.6

LABEL maintainer "Meltano Team <meltano@gitlab.com>"

# ---- Base image

# Install Google Cloud SDK
ENV CLOUD_SDK_REPO="cloud-sdk-stretch"
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y google-cloud-sdk

# TODO: use a sidecar
# Install Google SQL Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
RUN chmod +x /usr/bin/cloud_sql_proxy

# TODO: Port to 'click'
RUN pip install fire

# ---- Meltano image

# Installation dir
ADD src/meltano /app
RUN pip install /app

# Workdir
RUN mkdir /meltano
WORKDIR /meltano

CMD ["meltano"]