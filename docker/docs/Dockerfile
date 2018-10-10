FROM meltano/meltano/base
CMD ['bash']

COPY ./ ./

WORKDIR /meltano/docs
RUN pwd && pip install --upgrade pip && pip install -r requirements.txt
