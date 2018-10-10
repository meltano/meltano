FROM austinpray/python-node:3.7-10

# system deps
RUN apt-get update \
    && apt-get install -y gettext-base \
    && rm -rf /var/lib/apt/lists/*

ENV melt_workdir /meltano
WORKDIR ${melt_workdir}

# application deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ['python']
