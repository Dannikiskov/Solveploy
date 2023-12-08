#!/usr/bin/env python
import pika
import os
import sys

def on_request(ch, method, props, body):
    decoded_body = body.decode("utf-8")

    print(f" [.] message consumed! Got and {decoded_body} attempting reply to: result_{os.getenv('JOB_NAME')}", flush=True)

    result = f"new {decoded_body} who dis"
    
    ch.basic_publish(exchange='',
        routing_key=f"result-queue-{os.getenv('JOB_NAME')}",
        body=result)
    
    ch.stop_consuming()
    ch.queue_delete(queue=f"queue-{os.getenv('JOB_NAME')}")
    


if __name__ == '__main__':
    connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host='message-broker.default.svc.cluster.local',
                        credentials=pika.PlainCredentials(
                            os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))

    channel = connection.channel()
    channel.basic_consume(f"queue-{os.getenv('JOB_NAME')}", on_message_callback=on_request, auto_ack=True)

    print(f"Starting Consume from dynamic queue (queue-{os.getenv('JOB_NAME')})..", flush=True)
    
    channel.start_consuming()
    