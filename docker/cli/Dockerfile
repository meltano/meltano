FROM python:latest

COPY . /meltano

RUN pip install -r /meltano/requirements.txt && \
    pip install /meltano[cli]

WORKDIR /meltano_project

ENTRYPOINT ["meltano"]