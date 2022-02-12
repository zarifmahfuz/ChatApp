FROM python:3.8-slim-buster

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN mkdir /webserver
COPY . /webserver
WORKDIR /webserver
# RUN apk update && apk upgrade
# RUN apk add autoconf automake g++ make --no-cache
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "run"]