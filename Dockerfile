FROM ubuntu:latest

MAINTAINER Alberto Romeu "alrocar@carto.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential curl

COPY . /app
WORKDIR /app

ENV FLASK_APP=server.py

RUN pip3 install -r requirements.txt

CMD honcho start