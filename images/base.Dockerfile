FROM ubuntu:bionic

# -- Install deps
RUN apt-get update && \
    apt-get install -y python3.7 python3.7-dev python3-pip libpq-dev git nodejs curl gnupg && \
    pip3 install pipenv uwsgi gevent

# -- Install yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install -y yarn

# -- Set required environment variables for python
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# -- Add backend python code
ADD analyze/api /analyze
WORKDIR /analyze

# -- Install dependencies:
RUN pipenv install --deploy --system

# -- Install the needed nodejs dependencies that the python code shells out to
RUN git clone https://github.com/fabio-looker/node-lookml-parser.git && \
    mv node-lookml-parser parser && \
    cd parser && \
    yarn

# -- Build the static assets
ADD analyze /tmp

RUN cd /tmp && \
    yarn && \
    yarn run build && \
    mv /tmp/dist /analyze/app/static-assets && \
    rm -rf /tmp

CMD ["/usr/local/bin/uwsgi", "--gevent", "100", "--http", ":5000", "--module", "app:app", "--check-static", "/analyze/app/static-assets"]