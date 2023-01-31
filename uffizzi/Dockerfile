FROM python:3.9-slim

WORKDIR "/project"

RUN apt update
RUN apt-get install -y postgresql-client

COPY . .

ENV PIP_NO_CACHE_DIR=1

# Installing the application the same way our users do when using PyPI
RUN pip install --upgrade pip wheel
RUN pip install poetry
RUN poetry install
RUN mkdir /meltano

# Install zsh, ohmyzsh, ttyd
# Source: https://github.com/tsl0922/ttyd#install-on-linux
RUN apt update && apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev zsh curl fortune cowsay
RUN git clone https://github.com/tsl0922/ttyd.git /tmp/ttyd
RUN cd /tmp/ttyd && mkdir build && cd build && cmake .. && make install
# Source: https://ohmyz.sh/
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
ENV PATH="${PATH}:/usr/games"
# TTYD END
