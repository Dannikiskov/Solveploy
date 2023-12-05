#!/usr/bin/env python
import pika
import os
import solvers
import threading

class SolverResultQueue(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )
    
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='result-queue')
        self.channel.queue_declare(queue='job-queue')
        print(f"Queue declared", flush=True)
    
    def respond(self, data):
        self.channel.basic_publish(exchange='', routing_key='result-queue', body=data)
    
    def consume(self):
        def callback(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            print(f"Result received: {decoded_body}", flush=True)
            queue_name = solvers.start_solver_job(decoded_body)
            print(f"Publishing to dynamic queue ({queue_name})..", flush=True)
            ch.queue_declare(queue=queue_name)
            ch.basic_publish(exchange='', routing_key=queue_name, body=decoded_body)
            print(f"Success to ({queue_name})..", flush=True)
            threading.Thread(target=self.consume_from_dynamic_queue, args=(queue_name,)).start()


        self.channel.basic_consume(queue='job-queue', on_message_callback=callback, auto_ack=True)
        print("Starting Consume..", flush=True)
        self.channel.start_consuming()

    def consume_from_dynamic_queue(self, queue_name):
        connection_dynamic = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )
        
        def callback_dynamic(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            print(f"Dynamic queue: result_{queue_name} received: {decoded_body}", flush=True)
            
            ch.basic_publish(exchange='', routing_key=f"result-queue", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=f"result-{queue_name}")
            print("queue deleted", flush=True)

        channel_dynamic = connection_dynamic.channel()
        channel_dynamic.queue_declare(queue=f"result-{queue_name}")
        channel_dynamic.basic_consume(queue=f"result-{queue_name}", on_message_callback=callback_dynamic, auto_ack=True)
        print(f"Starting Consume from dynamic queue (result-{queue_name})..", flush=True)
        channel_dynamic.start_consuming()