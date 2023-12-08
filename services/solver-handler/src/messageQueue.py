#!/usr/bin/env python
import pika
import os
import solvers
import threading
import json
class SolverResultQueue(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )
    
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='request-queue')
        self.channel.queue_declare(queue="db-queue")
    
    def consume(self):
        def callback(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            message_data = json.loads(decoded_body)
            instructions = message_data.get('instructions', 'INSTREUCTION ERROR')
            identifier = message_data.get('identifier', "ID ERROR")
            print(f"sh.mq.consume: {message_data}", flush=True)

            queue_name = f'queue-{identifier}'
            ch.queue_declare(queue=queue_name)


            if instructions == "StartSolver":
                print("call start_and_pub_solver", flush=True)
                threading.Thread(target=self.start_and_pub_to_solver, args=(decoded_body, identifier,)).start()
            
            elif instructions == "GetSolverDBData":
                print("Dead end", flush=True)

            elif instructions == "PostSolverDBData":
                print("call post_to_db", flush=True)
                threading.Thread(target=self.post_to_solver_db, args=(decoded_body, identifier,)).start()

            else:
                print("FAILED: ", instructions, flush=True)
            


        self.channel.basic_consume(queue='request-queue', on_message_callback=callback, auto_ack=True)
        print("Starting Consume..", flush=True)
        self.channel.start_consuming()


    def consume_from_dynamic_queue(self, channel, identifier):

        result_queue_name = f"result-queue-{identifier}"
        print("RQN ", result_queue_name)

        def callback_dynamic(ch, method, properties, body):
            decoded_body = body.decode("utf-8")

            print(f"Dynamic queue: {result_queue_name} received: {decoded_body}", flush=True)

            ch.basic_publish(exchange='', routing_key=f"api-queue-{identifier}", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=result_queue_name)

        channel.queue_declare(queue=result_queue_name)
        channel.basic_consume(queue=result_queue_name, on_message_callback=callback_dynamic, auto_ack=True)

        print(f"Starting Consume from dynamic queue ({result_queue_name})..", flush=True)

        channel.start_consuming()
    

    def start_and_pub_to_solver(self, body, identifier):
        solvers.start_solver_job(identifier)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )

        queue_name = f"queue-{identifier}"
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.queue_declare(queue=f"result-{queue_name}")
        channel.basic_publish(exchange='', routing_key=queue_name, body=body)
        self.consume_from_dynamic_queue(channel, identifier)



    def post_to_solver_db(self, body, identifier):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        ) 
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key="db-queue", body=body)
        channel.queue_declare(queue=f"result-queue-{identifier}")
        self.consume_from_dynamic_queue(channel, identifier)