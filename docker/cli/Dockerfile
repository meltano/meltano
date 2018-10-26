FROM python:latest

# system deps
RUN apt-get update \
    && apt-get install -y gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY . /meltano

# defaut config files
COPY ./extract/singer/ /etc/singer/tap

RUN pip install -r /meltano/requirements.txt && \
    pip install /meltano[cli]

WORKDIR /meltano_project

ENTRYPOINT ["meltano"]