FROM registry.gitlab.com/meltano/meltano-elt/extract:latest

ENV SHELL=/bin/bash
WORKDIR /bizops
RUN pip3 install pipenv
RUN pipenv --site-packages
RUN pipenv install --dev --skip-lock