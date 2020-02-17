ARG BASE_IMAGE=meltano/meltano/base
FROM $BASE_IMAGE as builder

WORKDIR /meltano

# building the code
COPY . .

# this enables the build process to have access to local
# `meltano` module
ENV PYTHONPATH=src/
RUN make sdist

FROM $BASE_IMAGE as runtime
# grab the built package
COPY --from=builder /meltano/dist /meltano/dist

# install the built artifact to make sure we are
# installing the application the same way our user
# do when using PyPI
RUN pip install /meltano/dist/meltano-*.tar.gz

# copy the entrypoint
COPY docker/prod/entrypoint.sh /usr/local/bin/

# meltano project directory, this is where you should
# mount your Meltano project
WORKDIR /project

# make sure the webserver is online
HEALTHCHECK --interval=1m --timeout=1s \
  CMD kill -0 $(< .meltano/run/gunicorn.pid)

# meltano ui
EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["ui"]