FROM python:3.8-alpine

RUN mkdir /websocket
COPY . /websocket
WORKDIR /websocket
RUN pip install -r requirements.txt

EXPOSE 5200