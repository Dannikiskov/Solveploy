#!/usr/bin/env python
import pika
import os
import json
import satSolve
import time

if __name__ == '__main__':
    connection = None
    while not connection:
        try:
            established = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq.rabbitmq-system.svc.cluster.local',
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
    out_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}-result"
    channel.queue_declare(queue=in_queue_name, auto_delete=True)
    channel.queue_declare(queue=out_queue_name, auto_delete=True)
    
    outer_body = None

    def on_request(ch, method, props, body):
        global outer_body
        outer_body = body
        ch.stop_consuming()
    
    print(f"Starting Consume from dynamic queue ({in_queue_name})..", flush=True)
    channel.basic_consume(queue=in_queue_name, on_message_callback=on_request, auto_ack=True)
    channel.start_consuming()
    
    # Consume ends when msg consumed.
    channel.basic_publish(exchange='',
                        routing_key=in_queue_name,
                        body=outer_body,)
    channel.close()
    connection.close()

    decoded_body = outer_body.decode("utf-8")
    message_data = json.loads(decoded_body)

    print(f" [.] message consumed!", flush=True)
    solver_name = message_data["item"]["name"]
    print(f" [.] solver_name: {solver_name}", flush=True)
    params = json.loads(message_data["item"]["params"]) if "params" in message_data["item"] else None
    print(f" [.] params: {params}", flush=True)
    cnf_string = message_data["satFileContent"]
    if "cores" in message_data["item"]:
        cores = message_data["item"]["cores"]
    else:
        cores = None

    print("cores: ", cores, flush=True)

    try:
        print(f" [.] Running SAT Solver: {solver_name}", flush=True)
        result = satSolve.run_sat_model(solver_name.lower(), cnf_string,  cores, params)
        print(result, flush=True)
    except Exception as e:
        result = {"result": f"Sat Solver failed: {str(e)}", "executionTime": "N/A", "status": "ERROR"}

    result["name"] = solver_name
    result["satIdentifier"] = message_data["item"]["satIdentifier"]

    out_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}-result"
    json_result = json.dumps(result)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq.rabbitmq-system.svc.cluster.local',
            credentials=pika.PlainCredentials(
                os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
        )
    )
    channel = connection.channel()

    channel.basic_publish(exchange='',
                        routing_key=out_queue_name,
                        body=json_result)

    channel.basic_publish(exchange='',
                        routing_key="sat-result-queue",
                        body=json_result,)

    