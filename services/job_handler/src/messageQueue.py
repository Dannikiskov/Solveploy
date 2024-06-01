#!/usr/bin/env python
import base64
import pika
import os
import threading
import json
import time
import mznHandler
import satHandler
import maxsatHandler
import sunny
from multiprocessing import Process
from kubernetes import client, config
import k8sHandler as k8s

k8s_queues = []

def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="jobHandler")
    channel.queue_declare(queue="kbHandler")
    channel.queue_declare(queue="mzn-result-queue")
    channel.queue_declare(queue="sat-result-queue")
    channel.queue_declare(queue="maxsat-result-queue")
    channel.close()
    connection.close()

    
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
            threading.Thread(target=k8s.stop_specific_job, args=("mzn", data["identifier"],)).start()

        elif instructions == "StopSatJob":
            threading.Thread(target=k8s.stop_specific_job, args=("sat", data["identifier"],)).start()
        
        elif instructions == "StopMaxsatJob":
            threading.Thread(target=k8s.stop_specific_job, args=("maxsat", data["identifier"],)).start()
            
        elif instructions == "StopMznJobs":
            threading.Thread(target=k8s.stop_namespaced_jobs, args=("mzn",)).start()
        
        elif instructions == "StopSatJobs":
            threading.Thread(target=k8s.stop_namespaced_jobs, args=("sat",)).start()
        
        elif instructions == "StopMaxsatJobs":
            threading.Thread(target=k8s.stop_namespaced_jobs, args=("maxsat",)).start()
        
        elif instructions == "Sunny":
            data_content = data["dataContent"] if "dataContent" in data else None
            data_file_type = data["dataFileType"] if "dataFileType" in data else None
            threading.Thread(target=sunny.sunny, args=(data["fileContent"], data["solvers"], data["backupSolver"], data["k"], data["T"], data["identifier"], data["solverType"], data_content, data_file_type,)).start()

        else:
            print("ERROR: NO MATCHING INSTRUCTIONS:::", instructions, flush=True)
        


    channel.basic_consume(queue='jobHandler', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

def delete_k8_queues():
    global k8s_queues
    connection = _rmq_connect()
    for queue in k8s_queues:
        channel = connection.channel()
        channel.queue_delete(queue=queue)
        connection.close()

def send_wait_receive_k8(data, queue_name):
    global k8s_queues
    
    out_queue_name = queue_name
    in_queue_name = f'{out_queue_name}-result'

    k8s_queues.append(out_queue_name)
    k8s_queues.append(in_queue_name)

    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=out_queue_name)
    channel.queue_declare(queue=in_queue_name)

    json_data = json.dumps(data)

    channel.basic_publish(exchange='', routing_key=out_queue_name, body=json_data)

    result = None
    
    def callback(ch, method, properties, body):
        
        decoded_body = body.decode("utf-8")
        ch.queue_delete(queue=in_queue_name)
        nonlocal result
        result = json.loads(decoded_body)
        
        ch.stop_consuming()

    channel.basic_consume(queue=in_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    channel.queue_delete(queue=out_queue_name)
    channel.queue_delete(queue=in_queue_name)
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
    
    def callback(ch, method, properties, body):
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
    
    def callback(ch, method, properties, body):
        ch.stop_consuming()
        ch.queue_delete(queue=queue_name)
        decoded_body = body.decode("utf-8")
        nonlocal result
        result = decoded_body

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
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