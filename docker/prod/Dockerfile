ARG BASE_IMAGE=meltano/meltano/base
FROM $BASE_IMAGE as builder

WORKDIR /meltano

# building the code
COPY . .
RUN make sdist

FROM $BASE_IMAGE as runtime
# grab the built package
COPY --from=builder /meltano/dist /meltano/dist

# install the built artifact to make sure we are
# installing the application the same way our user
# do when using PyPI
RUN pip install /meltano/dist/meltano-*.tar.gz

# meltano project directory, this is where you should
# mount your Meltano project
WORKDIR /project

# meltano ui
EXPOSE 5000

# airflow ui
EXPOSE 5010

ENTRYPOINT ["meltano"]
CMD ["ui"]