FROM python:3.6 as builder
ENV NODE_VERSION 10

RUN echo "Installing system deps" \
    && apt-get update \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN echo "Installing node and yarn" \
    && curl -sS "https://deb.nodesource.com/setup_${NODE_VERSION}.x" | bash - \
    && curl -sS "https://dl.yarnpkg.com/debian/pubkey.gpg" | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y nodejs yarn \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# build requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt

# building
COPY . .
RUN make sdist

# runtime
FROM python:3.6
COPY --from=builder /build/dist /meltano/dist

# install the built artifact
# this makes sure we are installing the application the same
# way our user do using PyPI
RUN pip install /meltano/dist/meltano-*.tar.gz

# cleanup the build directory
RUN rm -rf /meltano

# meltano project directory, this is where you should
# mount your application volume
WORKDIR /project

# meltano ui
EXPOSE 5000

# airflow ui
EXPOSE 5010

ENTRYPOINT ["meltano"]
CMD ["ui"]