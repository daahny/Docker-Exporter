# Docker-Exporter
Docker-Exporter is a prometheus exporter written in python. It exports resource usage metrics of docker containers.

## Reasoning
Docker daemon does not export metrics like CPU usage and memory usage. cAdvisor is overkill for my purposes and was nearly impossible to configure correctly on my system.

## How docker-exporter works
Docker-Exporter is configured as a daemon on my Linux host. The script parses output from `docker stats --no-stream` and updates corresponding statistics on the prometheus exporter web page.

## Functionality
Currently, this script only exports CPU usage and memory usage.

![image](https://github.com/daahny/docker-exporter/assets/77124759/88274867-5ba3-4ba9-aade-ab7cea512733)
_Grafana view of docker container stats_
