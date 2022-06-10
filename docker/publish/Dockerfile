# Our recommended docker image for Meltano users.
#
# To reduce the size and security footprint of this image,
# many dev dependencies are intentionally excluded from this
# image.
#
# Required build-args:
# - PYTHON_VERSION: the version of python to use, e.g. '3.8', '3.9', etc.
# - MELTANO_VERSION: the version of Meltano to use, e.g. '1.105.0', '2.0.1', etc.

ARG PYTHON_VERSION

FROM python:$PYTHON_VERSION

ARG MELTANO_VERSION

# Probably not needed, but some devs may want these libraries
RUN echo "Installing system deps" \
    && apt-get update \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# installing the application the same way our users
# do when using PyPI
RUN pip install meltano==${MELTANO_VERSION}

# meltano project directory, this is where you should
# mount your Meltano project
WORKDIR /project

# meltano ui
EXPOSE 5000

ENTRYPOINT ["meltano"]
CMD ["ui"]
