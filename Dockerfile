FROM python:3.6.10-slim-buster

LABEL maintainer="Khoa Le <ltkhoa2711@gmail.com>"

RUN apt update && \
    apt install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV FLASK_ENV="docker"
EXPOSE 5000
