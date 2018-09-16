<<<<<<< HEAD
FROM registry.gitlab.com/meltano/meltano-cli:latest

ADD . /app/loader/postgresql

RUN pip install /app/loader/postgresql

=======
FROM registry.gitlab.com/meltano/meltano-load-postgresql

ADD . /app/extractor/fastly

RUN pip install /app/extractor/fastly

CMD meltano extract fastly | meltano load postgresql
>>>>>>> fastly/dev
