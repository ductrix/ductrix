FROM grafana/grafana
MAINTAINER Kevin Patel <kevin@ductrix.com>
COPY grafana.ini /etc/grafana/grafana.ini
RUN mkdir -p /var/lib/grafana/dashboards
COPY *.json /var/lib/grafana/dashboards/
RUN chown grafana:grafana /etc/grafana/grafana.ini
RUN chown grafana:grafana /var/lib/grafana/dashboards/*
RUN apt-get -qq update
RUN apt-get -qq -y install curl
