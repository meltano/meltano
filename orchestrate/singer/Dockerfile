# TODO: move to a more basic image
FROM registry.gitlab.com/meltano/meltano-elt/extract:latest

RUN pip3 install virtualenv

RUN virtualenv /venvs/tap-zendesk
RUN virtualenv /venvs/target-postgres

# TODO: version lock?
RUN /venvs/tap-zendesk/bin/pip install git+https://github.com/micaelbergeron/tap-zendesk.git@master
RUN /venvs/target-postgres/bin/pip install git+https://github.com/micaelbergeron/target-postgres.git@master

ENV SINGER_RUN_DIR /run/singer
RUN mkdir $SINGER_RUN_DIR

COPY ./orchestrate/singer/meltano-singer.sh /usr/bin
RUN chmod +x /usr/bin/meltano-singer.sh

# defaut config files
COPY ./extract/singer/ /etc/singer/tap
COPY ./load/singer /etc/singer/target

ENTRYPOINT ["meltano-singer.sh"]

CMD ["--help"]