import base64
import json
import pika
import os
import time
from kubernetes import client, config

def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="jobhandler")
    channel.queue_declare(queue="mzn-result-queue")
    channel.queue_declare(queue="sat-result-queue")
    channel.queue_declare(queue="maxsat-result-queue")
    channel.close()


# Service leaving call
def send_wait_receive(data):
    out_queue_name = data["queueName"]
    in_queue_name = f'{data["queueName"]}-{data["identifier"]}'

    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=in_queue_name, auto_delete=True)

    json_data = json.dumps(data)
    channel.basic_publish(exchange='', routing_key=out_queue_name, body=json_data)

    result = None

    # print(" [x] Sent")
    # print(" [*] Waiting for messages.")
    
    def callback(ch, method, properties, body):
        decoded_body = body.decode("utf-8")
        ch.queue_delete(queue=in_queue_name)
        nonlocal result
        result = decoded_body
        ch.stop_consuming()
        ch.queue_delete(queue=in_queue_name)

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return result

# Service leaving call
def send(data):
    out_queue_name = data["queueName"]

    connection = _rmq_connect()
    channel = connection.channel()

    json_data = json.dumps(data)
    channel.basic_publish(exchange='', routing_key=out_queue_name, body=json_data)
    connection.close()
    


def consume_one(queue_name):
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    result = None

    def callback(ch, method, properties, body):
        nonlocal result
        result = body.decode("utf-8")
        ch.stop_consuming()

    method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
    if method_frame:
        callback(channel, method_frame, None, body)
    else:
        return None
    
    return result

def _rmq_connect():
    # Load kube config
    config.load_incluster_config()

    v1 = client.CoreV1Api()

    # Get the secret
    secret = v1.read_namespaced_secret("rabbitmq", "default")

    # Decode the secret data
    password = base64.b64decode(secret.data['rabbitmq-password']).decode()

    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq.rabbitmq-system.svc.cluster.local',
                    credentials=pika.PlainCredentials('user', password)
                )
            )
        
        except Exception as e:
            print(f"Connection failed. Retrying in 5 seconds...", flush=True)
            print(e, flush=True)
            time.sleep(5)