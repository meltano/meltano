FROM meltano/meltano/runner

RUN pip install virtualenv

COPY . /meltano

RUN virtualenv /venvs/meltano
RUN virtualenv /venvs/tap-zendesk
RUN virtualenv /venvs/target-postgres

# TODO: version lock?
RUN /venvs/meltano/bin/pip install -r /meltano/requirements.txt && \
    /venvs/meltano/bin/pip install /meltano[cli]

RUN /venvs/tap-zendesk/bin/pip install tap-zendesk==1.4.0
RUN /venvs/target-postgres/bin/pip install git+https://github.com/micaelbergeron/target-postgres.git@master

ENV SINGER_RUN_DIR /run/singer
ENV SINGER_VENVS_DIR /venvs

RUN mkdir $SINGER_RUN_DIR

RUN ln -s /venvs/meltano/bin/meltano /usr/bin/meltano

# defaut config files
COPY ./extract/singer/ /etc/singer/tap
COPY ./load/singer /etc/singer/target

ENTRYPOINT ["meltano"]
