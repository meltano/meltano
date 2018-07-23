FROM registry.gitlab.com/meltano/meltano-cli:latest

ADD . /app/loader/postgresql

RUN pip install /app/loader/postgresql

