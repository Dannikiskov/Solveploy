#!/usr/bin/env python
import pika
import uuid
import os

class SolverJobQueue(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))
    
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='job-queue')
        self.channel.queue_declare(queue='result-queue')
        
    def publish(self, data):
        print("Attempting publish", flush=True)
        self.channel.basic_publish(exchange='', routing_key='job-queue', body=data)
    
    def consume(self):
        self.response = None
        def callback(ch, method, properties, body):
            print(f"Result recieved: {body}", flush=True)
            decoded_body = body.decode("utf-8")
            self.response = decoded_body
            self.channel.stop_consuming()
            print(f"Stopped consuming, returning body:  {decoded_body}", flush=True)
            

        self.channel.basic_consume(queue='result-queue', on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
        return self.response