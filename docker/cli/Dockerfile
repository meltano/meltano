FROM python:3.6

COPY . /meltano
WORKDIR /meltano

RUN pip install -r requirements.txt && \
    pip install .

ENTRYPOINT ["meltano"]