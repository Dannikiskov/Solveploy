#!/usr/bin/env python
import pika
import os
import threading
import json
import time
import mznHandler
import satHandler
import maxsatHandler

def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="jobHandler")
    channel.close()

    
def consume():
    channel = _rmq_connect().channel()
    def callback(ch, method, properties, body):
        decoded_body = body.decode("utf-8")
        data = json.loads(decoded_body)
        instructions = data["instructions"]

        if instructions == "StartMznJob":
            threading.Thread(target=mznHandler.handle_new_mzn_job, args=(data,)).start()

        elif instructions == "StartSatJob":
            threading.Thread(target=satHandler.handle_new_sat_job, args=(data,)).start()

        elif instructions == "StartMaxsatJob":
            threading.Thread(target=maxsatHandler.handle_new_maxsat_job, args=(data,)).start()

        elif instructions == "GetAvailableMznSolvers":
            threading.Thread(target=mznHandler.get_available_mzn_solvers, args=(data,)).start()
        
        elif instructions == "GetAvailableSatSolvers":
            threading.Thread(target=satHandler.get_available_sat_solvers, args=(data,)).start()
        
        elif instructions == "GetAvailableMaxsatSolvers":
            threading.Thread(target=maxsatHandler.get_available_maxsat_solvers, args=(data,)).start()
        
        elif instructions == "StopMznJob":
            threading.Thread(target=mznHandler.stop_job, args=(data,)).start()

        elif instructions == "StopSatJob":
            threading.Thread(target=satHandler.stop_job, args=(data,)).start()

        else:
            print("ERROR: NO MATCHING INSTRUCTIONS:::", instructions, flush=True)
        


    channel.basic_consume(queue='jobHandler', on_message_callback=callback, auto_ack=True)
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
        result = json.loads(decoded_body)
        
        ch.stop_consuming()

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return result


def send_wait_receive(data):
    out_queue_name = data["queueName"]
    in_queue_name = f'{data["queueName"]}-{data["identifier"]}'

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
        ch.stop_consuming()
        ch.queue_delete(queue=in_queue_name)
        decoded_body = body.decode("utf-8")
        nonlocal result
        result = decoded_body
        

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    return result


def send_to_queue(data, queue_name):
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    
    data = json.dumps(data)

    channel.basic_publish(exchange='', routing_key=queue_name, body=data)
    connection.close()

def consume_k8(queue_name):
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    result = None

    print(" [x] Sent")
    print(" [*] Waiting for messages.")
    
    def callback(ch, method, properties, body):
        print(" [*] Message received.")
        ch.stop_consuming()
        ch.queue_delete(queue=queue_name)
        decoded_body = body.decode("utf-8")
        nonlocal result
        result = decoded_body

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Starting Consume..", flush=True)
    channel.start_consuming()
    return result


def _rmq_connect():
    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='message-broker.default.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )
        except Exception as e:
            print(f"Connection failed. Retrying in 5 seconds...")
            time.sleep(5)