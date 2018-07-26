FROM python:3.6.6

LABEL maintainer "Meltano Team <meltano@gitlab.com>"

RUN set -ex && pip3 install pipenv --upgrade

ADD src/meltano /app/
WORKDIR /app

RUN pip install .

# TODO: use a sidecar
# Install Google SQL Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
RUN chmod +x /usr/bin/cloud_sql_proxy

CMD ["meltano"]