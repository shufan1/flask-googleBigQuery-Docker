# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /flaskBigQueryapp

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip install --upgrade google-cloud-bigquery
RUN pip install --upgrade gcloud

COPY . .

CMD [ "python", "app.py"]