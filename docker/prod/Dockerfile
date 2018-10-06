FROM meltano/meltano/base

RUN pip install uwsgi gevent

COPY ./ ./

RUN pip install -e '.[all]'

CMD ["python", "-m", "meltano.api"]
