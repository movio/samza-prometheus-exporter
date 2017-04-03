# -*- coding: utf-8 -*-

import json
import argparse
import time
import os
from samza_prometheus_exporter import samza
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Gauge, REGISTRY
from threading import Lock, Thread

KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'samza-prometheus-exporter')

GAUGES = {}
GAUGES_LAST_UPDATE = {}
GAUGES_LABELS_LAST_UPDATE = {}
GAUGES_LOCK = Lock()
GAUGES_TTL = 60

def metric_name_escape(name):
    return name.replace(".", "_").replace("-", "_").replace(" ", "_")

def setGaugeValue(name, labels, labelValues, value, description = ""):
    with GAUGES_LOCK:
        name = metric_name_escape(name)
        if name not in GAUGES:
            GAUGES[name] = Gauge(name, description, labels)
        if labels:
            GAUGES[name].labels(*labelValues).set(value)
            GAUGES_LABELS_LAST_UPDATE[(name, tuple(labelValues))] = time.time()
        else:
            GAUGES[name].set(value)
        GAUGES_LAST_UPDATE[name] = time.time()

def process_metric(host, job_name, container_name, task_name, metric_class_name, metric_name, metric_value):
    try:
        float(metric_value)
    except (TypeError, ValueError):
        return

    label_keys = [ 'host', 'samza_job', 'samza_container', 'samza_task' ]
    label_values = [ host, job_name, container_name, task_name ]

    if metric_class_name in samza.metrics:
        processed = False
        for entry in samza.metrics[metric_class_name]:
            if type(entry) is str and metric_name == entry:
                return setGaugeValue('samza:' + metric_class_name + ":" + metric_name, label_keys, label_values, metric_value)
            elif type(entry) is tuple:
                regex, parser = entry
                match = regex.match(metric_name)
                if match is not None:
                    parsed_metric = parser(match)
                    return setGaugeValue(
                        'samza:' + metric_class_name + ":" + parsed_metric['name'],
                        label_keys + list(parsed_metric['labels'].keys()),
                        label_values + list(parsed_metric['labels'].values()),
                        metric_value
                    )
        print('WARNING: unrecognized Samza metric: %s.%s' % (metric_class_name, metric_name))
    elif metric_class_name.startswith('org.apache.samza'):
        print('WARNING: unrecognized Samza metric: %s.%s' % (metric_class_name, metric_name))
    else:
        return setGaugeValue('samza:' + metric_class_name + ":" + metric_name, label_keys, label_values, metric_value)

def get_task_name(message_value_json):
    source = message_value_json['header']['source']
    if source.startswith('TaskName-'):
        return source[len('TaskName-'):]
    else:
        return "none"

def process_message(message, consumer, brokers):
    message_value_json = json.loads(str(message.value.decode('utf-8')))
    job_name = message_value_json['header']['job-name']
    container_name = message_value_json['header']['container-name']
    host = message_value_json['header']['host']
    task_name = get_task_name(message_value_json)
    for metric_class_name, metrics in message_value_json['metrics'].items():
        for metric_name, metric_value in metrics.items():
            process_metric(host, job_name, container_name, task_name, metric_class_name, metric_name, metric_value)

def consume_topic(consumer, brokers):
    print('Starting consumption loop.')
    for message in consumer:
        process_message(message, consumer, brokers)

def set_gauges_ttl(ttl):
    global GAUGES_TTL
    if ttl is not None: GAUGES_TTL = ttl

def start_ttl_watchdog_thread():
    t = Thread(target=ttl_watchdog)
    t.daemon = True
    t.start()

def ttl_watchdog_unregister_old_metrics(now):
    for (name, last_update) in list(GAUGES_LAST_UPDATE.items()):
        if now - last_update > GAUGES_TTL:
            REGISTRY.unregister(GAUGES[name])
            del GAUGES[name]
            del GAUGES_LAST_UPDATE[name]
            for (other_name, label_values) in list(GAUGES_LABELS_LAST_UPDATE.keys()):
                if name == other_name:
                    del GAUGES_LABELS_LAST_UPDATE[(name, label_values)]

def ttl_watchdog_remove_old_label_values(now):
    for ((name, label_values), last_update) in list(GAUGES_LABELS_LAST_UPDATE.items()):
        if now - last_update > GAUGES_TTL:
            GAUGES[name].remove(*label_values)
            del GAUGES_LABELS_LAST_UPDATE[(name, label_values)]

def ttl_watchdog():
    while True:
        time.sleep(GAUGES_TTL / 10.0)
        now = time.time()
        with GAUGES_LOCK:
            ttl_watchdog_unregister_old_metrics(now)
            ttl_watchdog_remove_old_label_values(now)

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
    parser.add_argument('--ttl', metavar='GAUGES_TTL', type=int, nargs='?',
                        help='time in seconds after which a metric (or label set) is no longer reported when not updated (default: 60s)')
    args = parser.parse_args()
    brokers = args.brokers.split(',')
    consumer = KafkaConsumer(args.topic, group_id=KAFKA_GROUP_ID, bootstrap_servers=brokers)
    start_http_server(args.port)

    set_gauges_ttl(args.ttl)

    if args.from_beginning:
        consumer.set_topic_partitions((args.topic, 0, 0)) # FIXME: beginning may not be offset 0

    start_ttl_watchdog_thread()

    try:
        consume_topic(consumer, args.brokers)
    except KeyboardInterrupt:
        pass # FIXME : should we close consumer ?

    print('Shutting down')
