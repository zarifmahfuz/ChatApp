FROM python:3.8-alpine

RUN mkdir /client
COPY . /client
WORKDIR /client

RUN apk update && apk upgrade
RUN apk --no-cache add curl
RUN pip install -r requirements.txt
