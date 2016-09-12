# samza-prometheus-exporter
Feed [Apache Samza](http://samza.apache.org/) metrics into [Prometheus](http://prometheus.io/)

![screenshot](https://raw.github.com/movio/samza-prometheus-exporter/master/images/samza-prometheus-exporter-screenshot.png)

# Installation
[This blog post](https://www.digitalocean.com/community/tutorials/how-to-install-prometheus-using-docker-on-ubuntu-14-04)
from Digital Ocean explains how to setup Prometheus, the node exporter and Grafana.

## Using docker

Build the docker image:

```
sudo docker build -t samza-prometheus-exporter:0.1.2 .
```

Then run it:

```
sudo docker run -d --name samza-prometheus-exporter -p 8080:8080 \
    -e "BROKERS=broker1:9092,broker2:9092" \
    -e "TOPIC=samza-metrics" \
    -e "PORT=8080" \
    samza-prometheus-exporter:0.1.2
```

## Using pip3
```
sudo pip3 install .
```
And then run `samza-prometheus-exporter`

# Hacking
To install the package in editable development mode:
```
sudo pip3 install -e .
```

# Acknowledgements
This project is heavily based on [prometheus-es-exporter](https://github.com/Braedon/prometheus-es-exporter)
