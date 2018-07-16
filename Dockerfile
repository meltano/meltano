FROM python:3.6.6

RUN set -ex && pip3 install pipenv --upgrade

ADD . /app/

WORKDIR /app

RUN set -ex && pipenv install --deploy --system

ENTRYPOINT python3 meltano