FROM python:3.6
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

WORKDIR /meltano

# application deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ['python']
