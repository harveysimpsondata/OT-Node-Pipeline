import subprocess
import json
import os
from confluent_kafka import Producer

import config


def read_logs():
    p = subprocess.Popen(["otnode-logs"], stdout=subprocess.PIPE, universal_newlines=True)

    while True:
        line = p.stdout.readline()
        if not line:
            break

        yield line.strip()  # remove newline

def parse_log(log):
    parts = log.split('] ', 1)  # split on the first "] "
    timestamp = parts[0][1:]  # remove the first "["
    level_message = parts[1]
    level, message = level_message.split(': ', 1)  # split on the first ": "

    return json.dumps({
        "timestamp": timestamp,
        "level": level,
        "message": message
    })

p = Producer({
    'bootstrap.servers': config.bootstrap_server,
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': os.getenv('CONFLUENT_USERNAME'),
    'sasl.password': os.getenv('CONFLUENT_PASSWORD')
})

def send_log(log):
    p.produce('MyTopic', parse_log(log))
    p.flush()  # make sure the logs are sent before the program exits

def main():
    for log in read_logs():
        send_log(log)

if __name__ == "__main__":
    main()
