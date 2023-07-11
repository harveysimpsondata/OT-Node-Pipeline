import subprocess
import json
import os
from confluent_kafka import Producer
import time
import re

def read_logs():
    cmd = ["journalctl", "-u", "otnode", "--output", "cat", "-f"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    while True:
        line = p.stdout.readline()
        if not line:
            break

        yield line.strip()  # remove newline

        time.sleep(1)

def parse_log(log):
    # Decode from Unicode to bytes, then from bytes to string with ASCII
    log = log.encode().decode('unicode_escape')

    parts = log.split('] ', 1)  # split on the first "] "
    timestamp = parts[0][1:]  # remove the first "["
    level_message = parts[1]
    level, message = level_message.split(': ', 1)  # split on the first ": "

    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    level = ansi_escape.sub('', level)
    message = ansi_escape.sub('', message)

    return json.dumps({
        "timestamp": timestamp,
        "level": level,
        "message": message
    })


p = Producer({
    'bootstrap.servers': "pkc-619z3.us-east1.gcp.confluent.cloud:9092",
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': os.getenv('CONFLUENT_USERNAME'),
    'sasl.password': os.getenv('CONFLUENT_PASSWORD')
})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def send_log(log):
    # Check if the log line has a timestamp in brackets
    if re.match(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', log):
        # The produce() function has an optional callback parameter which takes the delivery_report function
        p.produce('otnode-topic', parse_log(log), callback=delivery_report)

        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)

        p.flush()  # make sure the logs are sent before the program exits


def main():
    try:
        for log in read_logs():
            send_log(log)
    except KeyboardInterrupt:
        print('Stopping the producer...')
        p.flush()
        print('Producer stopped.')

if __name__ == "__main__":
    main()
