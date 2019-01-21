FROM python:3.6

COPY . /meltano
WORKDIR /meltano

RUN make bundle_models
RUN pip install -r requirements.txt && \
    pip install .

ENTRYPOINT ["meltano"]