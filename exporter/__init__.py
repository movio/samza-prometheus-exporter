# -*- coding: utf-8 -*-

import json
import argparse
from exporter import samza
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Gauge

KAFKA_GROUP_ID = 'samza-prometheus-exporter'

GAUGES = {}

def metric_name_escape(name):
    return name.replace(".", "_").replace("-", "_").replace(" ", "_")

def setGaugeValue(name, labels, labelValues, value, description = ""):
    name = metric_name_escape(name)
    if name not in GAUGES:
        GAUGES[name] = Gauge(name, description, labels)
    if labels:
        GAUGES[name].labels(*labelValues).set(value)
    else:
        GAUGES[name].set(value)

def process_metric(job_name, metric_class_name, metric_name, metric_value):
    try:
        float(metric_value)
    except ValueError:
        return
    if metric_class_name in samza.metrics:
        processed = False
        for entry in samza.metrics[metric_class_name]:
            if type(entry) is str and metric_name == entry:
                return setGaugeValue('samza:' + metric_class_name + ":" + metric_name, [ 'samza_job' ], [ job_name ], metric_value)
            elif type(entry) is tuple:
                regex, parser = entry
                match = regex.match(metric_name)
                if match is not None:
                    parsed_metric = parser(match)
                    return setGaugeValue(
                        'samza:' + metric_class_name + ":" + parsed_metric['name'],
                        [ 'samza_job' ] + list(parsed_metric['labels'].keys()),
                        [ job_name] + list(parsed_metric['labels'].values()),
                        metric_value
                    )
        raise KeyError('unrecognized Samza metric: %s.%s' % (metric_class_name, metric_name))
    else:
        return setGaugeValue('samza:' + metric_class_name + ":" + metric_name, [ 'samza_job' ], [ job_name ], metric_value)

def process_message(message, consumer, brokers):
    message_value_json = json.loads(str(message.value.decode('utf-8')))
    job_name = message_value_json['header']['job-name']
    for metric_class_name, metrics in message_value_json['metrics'].items():
        for metric_name, metric_value in metrics.items():
            process_metric(job_name, metric_class_name, metric_name, metric_value)

def consume_topic(consumer, brokers):
    print('Starting consumption loop.')
    for message in consumer:
        process_message(message, consumer, brokers)

def main():
    parser = argparse.ArgumentParser(description='Feed Apache Samza metrics into Prometheus.')
    parser.add_argument('--brokers', metavar='BROKERS', type=str, required=True,
                        help='list of comma-separated kafka brokers: host[:port],host[:port],...')
    parser.add_argument('--port', metavar='PORT', type=int, nargs='?', default=8080,
                        help='port to serve metrics to Prometheus (default: 8080)')
    parser.add_argument('--topic', metavar='TOPIC', type=str, nargs='?',default='samza-metrics',
                        help='name of topic to consume (default: "samza-metrics")')
    parser.add_argument('--from-beginning', action='store_const', const=True,
                        help='consume topic from offset 0')
    args = parser.parse_args()
    brokers = args.brokers.split(',')
    consumer = KafkaConsumer(args.topic, group_id=KAFKA_GROUP_ID, bootstrap_servers=brokers)
    start_http_server(args.port)

    if args.from_beginning:
        consumer.set_topic_partitions((args.topic, 0, 0)) # FIXME: beginning may not be offset 0

    try:
        consume_topic(consumer, args.brokers)
    except KeyboardInterrupt:
        pass # FIXME : should we close consumer ?

    print('Shutting down')
