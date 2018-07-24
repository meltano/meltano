FROM registry.gitlab.com/meltano/meltano-load-postgresql

ADD ../../meltano-extract-fastly /app/extract/fastly

RUN pip install /app/extract/fastly

CMD set -o pipefail && meltano extract fastly | meltano load postgresql