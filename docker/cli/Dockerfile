FROM python:latest

COPY . /meltano

# defaut config files
COPY ./extract/singer/ /etc/singer/tap

RUN pip install -r /meltano/requirements.txt && \
    pip install /meltano[cli]

WORKDIR /meltano_project

ENTRYPOINT ["meltano"]