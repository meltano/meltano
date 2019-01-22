ARG BASE_IMAGE=meltano/meltano/base
FROM $BASE_IMAGE

COPY ./ ./

RUN make bundle
RUN pip install -e .

EXPOSE 5000

CMD ["meltano", "ui"]
