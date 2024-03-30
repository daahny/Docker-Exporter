# main.py

import re
import subprocess
import time
import os
import sys
import logging
from systemd.journal import JournalHandler
from prometheus_client import start_http_server, Gauge
from container import Container

current_containers = {}
cpu_gauge = Gauge('container_cpu_usage', 'CPU usage of container as a percentage', labelnames=['id', 'name'])
memory_gauge = Gauge('container_memory_usage', 'Memory usage of container as a percentage', labelnames=['id', 'name'])
log = None
port = 4000


def docker_stats():
    '''Return formatted output from `docker stats`'''

    p = subprocess.Popen(['/bin/sh', '-c', '/usr/bin/docker stats --no-stream'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    return out.decode('utf-8').split('\n', 1)[1].splitlines()


def return_containers_dict() -> dict:
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


def update_gauges(current_containers, new_containers):
    '''Restart script if a container has been removed'''

    for id in current_containers.keys():
        if id not in new_containers.keys():
            log.warning(f'Container {current_containers[id].name} is no longer running.')
            log.warning('Restarting Docker-Exporter.')
            python_interpreter = sys.executable
            os.execv(python_interpreter, ['python'] + sys.argv)



def update_containers_dict() -> dict:
    '''Returns updated containers dict'''

    new_containers = return_containers_dict()
    new_containers = check_containers_down(new_containers)

    return new_containers


def check_containers_down(new_containers: dict):
    '''Checks if any containers are running. Waits for containers to start if not. Returns updated containers dict when up.'''

    if len(new_containers) == 0:
        log.warning('Detected docker containers are down.')
        log.info('Waiting for containers to come back up.')

        while True:
            time.sleep(15)
            new_containers = return_containers_dict()

            if len(new_containers) == 0:
                continue
            else:
                log.info('Docker containers detected.')
                log.info('Resuming monitoring.')
                return new_containers
            
    return new_containers


def update_stats():
    '''Update statistics of gauges'''

    global current_containers
    new_containers = update_containers_dict()

    if current_containers.keys() != new_containers.keys():
        update_gauges(current_containers, new_containers)

    for id in new_containers.keys():
        name = new_containers[id].name
        cpu = new_containers[id].cpu
        memory = new_containers[id].memory

        cpu_gauge.labels(id=id, name=name).set(cpu)
        memory_gauge.labels(id=id, name=name).set(memory)
    
    current_containers = new_containers


def init_logger():
    '''Init logging handler'''

    global log
    log = logging.getLogger('docker-exporter')
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)


def init():
    '''Start exporter daemon and set initial container values'''

    init_logger()

    log.info('Log handler initalized.')
    log.info(f'Starting HTTP server on port {port}.')
    start_http_server(port)

    log.info('Running docker stats for the first time.')
    global current_containers
    current_containers = return_containers_dict()

    log.info('Monitoring docker stats every 15 seconds.')
    while True:
        update_stats()
        time.sleep(15)


init()