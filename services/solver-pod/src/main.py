#!/usr/bin/env python
import pika
import os
import json
import minizincSolve
import time

def on_request(ch, method, props, body):
    decoded_body = body.decode("utf-8")
    message_data = json.loads(decoded_body)

    print(f" [.] message consumed! Got and {decoded_body} attempting reply to: result_{os.getenv('JOB_NAME')}", flush=True)
    model_string = message_data.get('model', "MODEL ERROR")
    print("MODEL STRING: ", model_string, flush=True)
    try:
        result = minizincSolve.run_minizinc_model(model_string)
    except:
        result = "Minizinc solver Failed."
    
    ch.basic_publish(exchange='',
        routing_key=f"result-queue-{os.getenv('JOB_NAME')}",
        body=result)
    
    ch.stop_consuming()
    ch.queue_delete(queue=f"queue-{os.getenv('JOB_NAME')}")
    


if __name__ == '__main__':
    connection = None
    while not connection:
        try:
            established = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='message-broker.default.svc.cluster.local',
                    credentials=pika.PlainCredentials(
                        os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
                )
            )
            print("Connection established successfully.", flush=True)
            connection = established
            
        except pika.exceptions.AMQPConnectionError:
            print("Connection failed. Retrying in 5 seconds...", flush=True)
            time.sleep(5)

    channel = connection.channel()
    channel.basic_consume(f"queue-{os.getenv('JOB_NAME')}", on_message_callback=on_request, auto_ack=True)

    print(f"Starting Consume from dynamic queue (queue-{os.getenv('JOB_NAME')})..", flush=True)
    
    channel.start_consuming()
    connection.close()
    