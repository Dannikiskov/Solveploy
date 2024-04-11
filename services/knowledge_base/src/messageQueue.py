#!/usr/bin/env python
import pika
import os
import json
import time
import database


def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="kbHandler")
    channel.close()

    
def consume():
    channel = _rmq_connect().channel()
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body, flush=True)
        decoded_body = body.decode("utf-8")
        data = json.loads(decoded_body)
        instructions = data["instructions"]
        content = data.get("content", "FAILED TO RETRIEVE CONTENT IN MQ KB")
        queue_name = data.get("queueName", "FAILED TO RETRIEVE QUEUE NAME IN MQ KB")
        identifier = data.get("identifier", "FAILED TO RETRIEVE IDENTIFIER IN MQ KB")
        

        if instructions == "GetAllMznFeatureVectors":
            response = database.get_all_mzn_feature_vectors()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetAllSatFeatureVectors":
            response = database.get_all_sat_feature_vectors()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "HandleMznInstance":
            response = database.handle_mzn_instance(data)
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "HandleSatInstance":
            response = database.handle_sat_instance(data)
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetSolved":
            response = database.get_solved(content['solvers'], content['similarInsts'], content['T'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetSolvedTimesMzn":
            response = database.get_solved_times_mzn(content['solverName'], content['similarInsts'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "GetSolvedTimesSat":
            response = database.get_solved_times_sat(content['solverName'], content['similarInsts'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "GetSolvedTimesMaxSat":
            response = database.get_solved_times_maxsat(content['solverName'], content['similarInsts'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "GetSolvers":
            response = database.get_solvers()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "SetAllocatableResources":
            response = database.set_allocatable_resources(data)
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "UpdateInUseResources":
            response = database.update_in_use_resources()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetAvailableK8sResources":
            response = database.get_available_k8s_resources()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        else:
            print("FAILED - No matching instructions: ", instructions, flush=True)
        


    channel.basic_consume(queue='kbHandler', on_message_callback=callback, auto_ack=True)
    print("Starting Consume..", flush=True)
    channel.start_consuming()



def send_to_queue(data, queue_name):
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=data)
    connection.close()


def _rmq_connect():
    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='message-broker.rabbitmq-system.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )
        except Exception as e:
            print(f"Connection failed. Retrying in 5 seconds...")
            time.sleep(5)