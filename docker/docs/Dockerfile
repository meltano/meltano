ARG BASE_IMAGE=meltano/meltano/base
FROM $BASE_IMAGE

CMD ['bash']

COPY ./ ./

WORKDIR /meltano/docs
RUN pwd && pip install --upgrade pip && pip install -r requirements.txt
