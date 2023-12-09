#!/usr/bin/env python
import pika
import uuid
import os
import json
class RequestQueue(object):
    def __init__(self, identifier):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))
        
        self.identifier = identifier
        self.res_queue = f'api-queue-{self.identifier}'
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='request-queue')
        self.channel.queue_declare(queue="db-queue")
        self.channel.queue_declare(queue=self.res_queue)

    def publish(self, data):
        print("SENDING:::", flush=True)
        json_data = json.dumps(data)
        self.channel.basic_publish(exchange='', routing_key='request-queue', body=json_data)

    
    def consume(self):
        self.response = None
        def callback(ch, method, properties, body):
            print(f"Result recieved: {body}", flush=True)
            decoded_body = body.decode("utf-8")
            self.response = decoded_body
            ch.stop_consuming()
            ch.queue_delete(queue=self.res_queue)
            
        self.channel.basic_consume(queue=self.res_queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
        self.connection.close()
        return self.response