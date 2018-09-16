FROM registry.gitlab.com/meltano/meltano-load-postgresql

ADD . /app/extractor/fastly

RUN pip install /app/extractor/fastly

CMD meltano extract fastly | meltano load postgresql
