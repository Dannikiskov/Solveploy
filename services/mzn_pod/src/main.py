#!/usr/bin/env python
import pika
import os
import json
import minizincSolve
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
            connection = established
            
        except pika.exceptions.AMQPConnectionError:
            print("Connection failed. Retrying in 5 seconds...", flush=True)
            time.sleep(5)

    channel = connection.channel()
    in_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}"
    out_queue_name = f"solverk8job-{os.getenv('IDENTIFIER')}-result"
    channel.queue_declare(queue=in_queue_name)
    channel.queue_declare(queue=out_queue_name)
    
    outer_body = None

    def on_request(ch, method, props, body):
        global outer_body
        outer_body = body
        ch.stop_consuming()
    
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

    solver_name = message_data["item"]["name"]
    params = json.loads(message_data["item"]["params"]) if "params" in message_data["item"] else None
    mzn_string = message_data["mznFileContent"]
    data_string = message_data["dataFileContent"] if message_data["dataFileContent"] != "" else None
    data_type = message_data["dataFileType"] if message_data["dataFileType"] != "" else None
    opt_goal = message_data["optGoal"] if message_data["optGoal"] != "" else None

    try:
        result = minizincSolve.run_minizinc_model(mzn_string, solver_name.lower(), data_string, data_type, params)
        
    except Exception as e:
        result = {"result": f"Minizinc Solver failed: {str(e)}", "executionTime": "N/A", "status": "ERROR"}
        
    result["name"] = solver_name
    result["optGoal"] = opt_goal if opt_goal is not None else "N/A"
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
                        routing_key="mzn-result-queue",
                        body=json_result,)

    