# samza-prometheus-exporter
Feed [Apache Samza](http://samza.apache.org/) metrics into [Prometheus](http://prometheus.io/)

# Installation
[This blog post](https://www.digitalocean.com/community/tutorials/how-to-install-prometheus-using-docker-on-ubuntu-14-04) from Ditial Ocean explains how to setup Prometheus.
The easiest is to run the docker image. Specify the `PORT`, `BROKERS` and `TOPIC` env variables when running the image.
To run outside docker, install with:
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
