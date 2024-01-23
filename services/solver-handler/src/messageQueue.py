#!/usr/bin/env python
import pika
import os
import threading
import json
import time
import solverHandler

def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="solverhandler")
    channel.close()

    
def consume():
    channel = _rmq_connect().channel()
    def callback(ch, method, properties, body):
        decoded_body = body.decode("utf-8")
        data = json.loads(decoded_body)
        instructions = data.get('instructions', 'DICT INSTRUCTION ERROR')

        if instructions == "StartSolver":
            threading.Thread(target=solverHandler.solver_handler, args=(data,)).start()

        else:
            print("FAILED: ", instructions, flush=True)
        


    channel.basic_consume(queue='solverhandler', on_message_callback=callback, auto_ack=True)
    print("Starting Consume..", flush=True)
    channel.start_consuming()


def send_wait_receive_k8(data, queue_name):
    out_queue_name = queue_name
    in_queue_name = f'{out_queue_name}-result'

    connection = _rmq_connect()
    channel = connection.channel()
    print("declaring queue: ", out_queue_name, flush=True)
    channel.queue_declare(queue=out_queue_name)
    print("declaring queue: ", in_queue_name, flush=True)
    channel.queue_declare(queue=in_queue_name)

    channel.basic_publish(exchange='', routing_key=out_queue_name, body=data)

    result = None

    print(" [x] Sent")
    print(" [*] Waiting for messages.")
    
    def callback(ch, method, properties, body):
        
        print(" [*] Message received.")
        decoded_body = body.decode("utf-8")
        ch.queue_delete(queue=in_queue_name)
        nonlocal result
        result = decoded_body
        ch.stop_consuming()

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return result


def send_wait_receive(data):
    out_queue_name = data["queue_name"]
    in_queue_name = f'{data["queue_name"]}-{data["identifier"]}'

    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=in_queue_name)

    json_data = json.dumps(data)
    channel.basic_publish(exchange='', routing_key=out_queue_name, body=json_data)

    result = None

    print(" [x] Sent")
    print(" [*] Waiting for messages.")
    
    def callback(ch, method, properties, body):
        
        print(" [*] Message received.")
        decoded_body = body.decode("utf-8")
        ch.queue_delete(queue=in_queue_name)
        nonlocal result
        result = decoded_body
        ch.stop_consuming()

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return result


def send_to_queue(data, queue_name):
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=data)
    connection.close()


def _rmq_connect():
    max_retries = 20
    retries = 0
    while retries < max_retries:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='message-broker.default.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )
        except Exception as e:
            print(f"Connection failed. Retrying in 5 seconds... ({retries+1}/{max_retries})")
            retries += 1
            time.sleep(5)
    print("Connection failed after maximum retries.")
    return None