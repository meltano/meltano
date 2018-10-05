FROM meltano/meltano/base

RUN pip install uwsgi gevent

COPY ./ ./

RUN pip install -e .[api]

CMD ["python", "-m", "meltano.api"]
