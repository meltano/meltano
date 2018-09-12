FROM austinpray/python-node:3.7-10

ENV melt_workdir /meltano
WORKDIR ${melt_workdir}

ENV PYTHONPATH ${melt_workdir}/plugins

COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ['python']
