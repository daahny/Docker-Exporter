# main.py

import re
import subprocess
import time
from prometheus_client import start_http_server, Gauge
from container import Container


cpu_gauge = Gauge('container_cpu_usage', 'CPU usage of container as a percentage', labelnames=['id', 'name'])
memory_gauge = Gauge('container_memory_usage', 'Memory usage of container as a percentage', labelnames=['id', 'name'])


def docker_stats():
    '''Return formatted output from `docker stats`'''

    p = subprocess.Popen(['/bin/sh', '-c', '/usr/bin/docker stats --no-stream'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    return out.decode('utf-8').split('\n', 1)[1].splitlines()
    

def remove_gauges(current_containers, new_containers):
    '''Set gauges of no longer running containers to -1'''

    for id in current_containers.keys():
        if id not in new_containers.keys():
            name = current_containers[id].name

            cpu_gauge.labels(id=id, name=name).set(-1)
            memory_gauge.labels(id=id, name=name).set(-1)


def update_containers(current_containers):
    '''Updates containers dict'''

    new_containers = return_containers_dict()

    if current_containers.keys() != new_containers.keys():
        remove_gauges(current_containers, new_containers)

    return new_containers


def update_stats(current_containers):
    '''Update statistics of gauges'''

    containers = update_containers(current_containers)

    for id in containers.keys():
        name = containers[id].name
        cpu = containers[id].cpu
        memory = containers[id].memory
        
        cpu_gauge.labels(id=id, name=name).set(cpu) 
        memory_gauge.labels(id=id, name=name).set(memory)


def return_containers_dict():
    '''Returns containers dict using data from `docker stats`'''

    containers = {}
    for line in docker_stats():
        container = re.split(r'\s{2,}', line)

        id = container[0]
        name = container[1]
        cpu = container[2].replace('%', '')
        memory = container[4].replace('%', '')
        containers[id] = Container(id, name, cpu, memory)

    return containers


def init():
    '''Start exporter daemon and set initial container values'''

    start_http_server(4000)
    current_containers = return_containers_dict() 

    while True:
        update_stats(current_containers)
        time.sleep(15)


init()