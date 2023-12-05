#!/usr/bin/env python
import pika
import os
import sys

def on_request(ch, method, props, body):
    print(f" [.] message consumed! Got and {body} attempting reply to: result_{os.getenv('JOB_NAME')}", flush=True)
    result = f"new {body} who dis"
    ch.basic_publish(exchange='',
        routing_key=f"result-{os.getenv('JOB_NAME')}",
        body=result)
    ch.stop_consuming()
    ch.queue_delete(queue=os.getenv('JOB_NAME'))
    


if __name__ == '__main__':
    connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='message-broker.default.svc.cluster.local',
                        credentials=pika.PlainCredentials(
                            os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))

    channel = connection.channel()
    channel.basic_consume(os.getenv("JOB_NAME"), on_message_callback=on_request, auto_ack=True)
    print(f"Starting Consume from dynamic queue ({os.getenv('JOB_NAME')})..", flush=True)
    channel.start_consuming()
    