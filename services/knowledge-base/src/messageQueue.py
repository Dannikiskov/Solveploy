#!/usr/bin/env python
import pika
import os
import threading
import json
import time
import database

def rmq_init():
    connection = _rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue="knowledge-base")
    channel.close()

    
def consume():
    channel = _rmq_connect().channel()
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body, flush=True)
        decoded_body = body.decode("utf-8")
        data = json.loads(decoded_body)
        instructions = data.get('instructions', 'DICT INSTRUCTION ERROR')
        content = data.get('content', None)
        queue_name = data.get('queue_name', "DICT QUEUE NAME ERROR")
        identifier = data.get('identifier', "DICT IDENTIFIER ERROR")
        

        if instructions == "GetAllFeatureVectors":
            response = database.get_all_feature_vectors()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "HandleInstance":
            response = database.handle_instance(data)
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetSolved":
            response = database.get_solved(content['solvers'], content['similar_insts'], content['T'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))
        
        elif instructions == "GetSolvedTimes":
            response = database.get_solved_times(content['solver_id'], content['similar_insts'])
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        elif instructions == "GetSolvers":
            response = database.get_solvers()
            ch.basic_publish(exchange='', routing_key=f'{queue_name}-{identifier}', body=json.dumps(response))

        else:
            print("FAILED: ", instructions, flush=True)
        


    channel.basic_consume(queue='knowledge-base', on_message_callback=callback, auto_ack=True)
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
                    host='message-broker.default.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )
        except Exception as e:
            print(f"Connection failed. Retrying in 5 seconds...")
            time.sleep(5)