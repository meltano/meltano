FROM python:3.7

WORKDIR /marketo

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . ./

RUN pip install -e .
