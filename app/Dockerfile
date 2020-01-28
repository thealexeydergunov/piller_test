FROM python:3.7.4-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/app/