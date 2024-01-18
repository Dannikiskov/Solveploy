#!/usr/bin/env python
import pika
import os
import solverK8Job
import threading
import json
import time
import solverHandler
class SolverResultQueue(object):
    def __init__(self):
        self.connection = None
        while not self.connection:
            try:
                established = rmq_connect()
                print("Connection established successfully.", flush=True)
                self.connection = established

            except pika.exceptions.AMQPConnectionError:
                print("Connection failed. Retrying in 5 seconds...", flush=True)
                time.sleep(5)

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='request-queue')
        self.channel.queue_declare(queue="db-queue")
    
    def consume(self):
        def callback(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            message_data = json.loads(decoded_body)
            instructions = message_data.get('instructions', 'INSTRUCTION ERROR')
            identifier = message_data.get('identifier', "ID ERROR")
            print(f"sh.mq.consume: {message_data}", flush=True)

            queue_name = f'queue-{identifier}'
            ch.queue_declare(queue=queue_name)


            if instructions == "StartSolver":
                print("call start_solver", flush=True)

                threading.Thread(target=solverHandler.solver_handler, args=(message_data,)).start()

            else:
                print("FAILED: ", instructions, flush=True)
            


        self.channel.basic_consume(queue='request-queue', on_message_callback=callback, auto_ack=True)
        print("Starting Consume..", flush=True)
        self.channel.start_consuming()


    def consume_from_dynamic_queue(self, channel, identifier):

        result_queue_name = f"result-queue-{identifier}"
        print("RQN ", result_queue_name)

        def callback_dynamic(ch, method, properties, body):
            decoded_body = body.decode("utf-8")

            print(f"Dynamic queue: {result_queue_name} received: {decoded_body}", flush=True)

            ch.basic_publish(exchange='', routing_key=f"api-queue-{identifier}", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=result_queue_name)

        channel.queue_declare(queue=result_queue_name)
        channel.basic_consume(queue=result_queue_name, on_message_callback=callback_dynamic, auto_ack=True)

        print(f"Starting Consume from dynamic queue ({result_queue_name})..", flush=True)

        channel.start_consuming()
    



def rmq_connect():
    return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='message-broker.default.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )

def consume_from_dynamic_queue(channel, identifier):

        result_queue_name = f"result-queue-{identifier}"
        print("RQN ", result_queue_name)

        def callback_dynamic(ch, method, properties, body):
            decoded_body = body.decode("utf-8")

            print(f"Dynamic queue: {result_queue_name} received: {decoded_body}", flush=True)

            ch.basic_publish(exchange='', routing_key=f"api-queue-{identifier}", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=result_queue_name)

        channel.queue_declare(queue=result_queue_name)
        channel.basic_consume(queue=result_queue_name, on_message_callback=callback_dynamic, auto_ack=True)

        print(f"Starting Consume from dynamic queue ({result_queue_name})..", flush=True)

        channel.start_consuming()

def pub_to_queue(data, queue_name):
    connection = rmq_connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=data)
    connection.close()