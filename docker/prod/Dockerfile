FROM meltano/meltano/base

RUN pip install uwsgi gevent

COPY ./ ./

RUN make build_templates
RUN pip install -e .

EXPOSE 5000

CMD ["meltano", "www"]
