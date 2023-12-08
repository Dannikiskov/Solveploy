import pika
import os
import json

class DBQueue(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))
        
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='db-queue')
    
    def consume(self):
        def callback(ch, method, properties, body):

            print(f"Result recieved: {body}", flush=True)

            decoded_body = body.decode("utf-8")

            print(f"decoded body: {body}", flush=True)

            message_data = json.loads(decoded_body)

            identifier = message_data.get('identifier', "ID ERROR")

            print("identifier:", identifier, flush=True)

            ch.basic_publish(exchange='',
                routing_key=f"result-queue-{identifier}",
                body=f"this is from DB: {decoded_body}")
            
            print(f"Sent to: result-queue-{identifier}", flush=True)
            
            
        self.channel.basic_consume(queue="db-queue", on_message_callback=callback, auto_ack=True)
        print("COMSUMING", flush=True)
        self.channel.start_consuming()

if __name__ == '__main__':
    db_queue = DBQueue()
    db_queue.consume()