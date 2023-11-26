#!/usr/bin/env python
import pika, os

def main():

    rabbitmq_username = os.getenv("RABBITMQ_USERNAME")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
    print(rabbitmq_username, flush=True)
    print(rabbitmq_password, flush=True)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='message-broker.default.svc.cluster.local', credentials=pika.PlainCredentials(rabbitmq_username, rabbitmq_password)))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}", flush=True)

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C', flush=True)
    channel.start_consuming()

if __name__ == '__main__':
    print("Calling main", flush=True)
    main()