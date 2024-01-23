#!/usr/bin/env python
import pika
import os
import json
import minizincSolve
import time


def on_request(ch, method, props, body):
    decoded_body = body.decode("utf-8")
    message_data = json.loads(decoded_body)
    print(f" [.] message consumed! Got and\n-------------\n {message_data} \n-------------", flush=True)
    model_string = message_data.get('content', "CONTENT ERROR")
    
    print("MODEL STRING: ", model_string, flush=True)
    try:
        result = minizincSolve.run_minizinc_model(model_string)
    except:
        result = "Minizinc solver Failed."
    
    out_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}-result"

    ch.basic_publish(exchange='',
        routing_key=out_queue_name,
        body=result)
    
    ch.stop_consuming()
    ch.queue_delete(queue=out_queue_name)
    


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
    in_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}"
    channel.basic_consume(queue=in_queue_name, on_message_callback=on_request, auto_ack=True)

    print(f"Starting Consume from dynamic queue ({in_queue_name})..", flush=True)
    
    channel.start_consuming()
    connection.close()
    