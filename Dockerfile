FROM python:3-slim

MAINTAINER nicolas@movio.co

WORKDIR /usr/src/app

COPY exporter/*.py /usr/src/app/exporter/
COPY setup.py /usr/src/app/
COPY LICENSE /usr/src/app/

RUN pip install -e .

ENV PORT=8080
ENV BROKERS=dockerhost
ENV TOPIC=samza-metrics

CMD python -u /usr/local/bin/samza-prometheus-exporter --brokers $BROKERS --port $PORT --topic $TOPIC
