ARG BASE_IMAGE=meltano/meltano/base
FROM $BASE_IMAGE as builder

WORKDIR /meltano

# building the code
COPY . .
# RUN make sdist

# install the built artifact
# this makes sure we are installing the application the same
# way our user do using PyPI
#RUN pip install /meltano/dist/meltano-*.tar.gz
RUN pip install .

# meltano project directory, this is where you should
# mount your Meltano project
WORKDIR /project

# meltano ui
EXPOSE 5000

# airflow ui
EXPOSE 5010

ENTRYPOINT ["meltano"]
CMD ["ui"]