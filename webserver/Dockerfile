FROM python:3.8-alpine

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN mkdir /webserver
COPY . /webserver
WORKDIR /webserver
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "run"]