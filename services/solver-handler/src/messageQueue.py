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
    
    def consume(self):
        def callback(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            message_data = json.loads(decoded_body)
            instructions = message_data.get('instructions', 'INSTREUCTION ERROR')
            identifier = message_data.get('identifier', "ID ERROR")
            print(f"sh.mq.consume: {message_data}, {instructions}, {identifier} ", flush=True)

            if instructions == "StartSolver":
                print("call start_and_pub_solver", flush=True)
                self.start_and_pub_to_solver(ch, decoded_body, identifier)
            
            elif instructions == "GetSolverDBData":
                print("Dead end")

            elif instructions == "PostSolverDBData":
                print("call post_to_db", flush=True)
                self.post_to_solver_db(ch, decoded_body, identifier)

            else:
                print("FAILED: ", instructions, flush=True)
            


        self.channel.basic_consume(queue='request-queue', on_message_callback=callback, auto_ack=True)
        print("Starting Consume..", flush=True)
        self.channel.start_consuming()

    def consume_from_db_result_queue(self, db_queue_name, identifier):
        connection_dynamic = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )

        print("conn estab. ", flush=True)

        def db_callback_dynamic(ch, method, properties, body):
            decoded_body = body.decode("utf-8")
            print(f"Dynamic queue: {db_queue_name} received: {decoded_body}", flush=True)
            ch.basic_publish(exchange='', routing_key=f"res-queue-{identifier}", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=f"{db_queue_name}")

        channel_dynamic = connection_dynamic.channel()
        channel_dynamic.queue_declare(queue=db_queue_name)
        channel_dynamic.basic_consume(queue=db_queue_name, on_message_callback=db_callback_dynamic, auto_ack=True)
        print(f"Declared: {db_queue_name}")
        print(f"Starting Consume from dynamic queue ({db_queue_name})..", flush=True)
        channel_dynamic.start_consuming()

    
    def consume_from_solver_result_queue(self, solver_queue_name, identifier):
        connection_dynamic = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))
            )
        )

        print("conn estab. ", flush=True)

        def callback_dynamic(ch, method, properties, body):
            print("conn estab. ", flush=True)
            decoded_body = body.decode("utf-8")
            print(f"Dynamic queue: result-{solver_queue_name} received: {decoded_body}", flush=True)
            ch.basic_publish(exchange='', routing_key=f"res-queue-{identifier}", body=decoded_body)
            ch.stop_consuming()
            ch.queue_delete(queue=f"result-{solver_queue_name}")

        channel_dynamic = connection_dynamic.channel()
        channel_dynamic.queue_declare(queue=f"result-{solver_queue_name}")
        channel_dynamic.basic_consume(queue=f"result-{solver_queue_name}", on_message_callback=callback_dynamic, auto_ack=True)
        print(f"Starting Consume from dynamic queue (result-{solver_queue_name})..", flush=True)
        channel_dynamic.start_consuming()
    

    def start_and_pub_to_solver(self, ch, body, identifier):
        print(f"call solv_star_j", flush=True)
        solver_queue_name = solvers.start_solver_job(identifier)
        print(f"sol_q_name: {solver_queue_name}", flush=True)
        ch.queue_declare(queue=solver_queue_name)
        ch.basic_publish(exchange='', routing_key=solver_queue_name, body=body)
        print(f"starting cons_f_sol_res_q", flush=True)
        threading.Thread(target=self.consume_from_solver_result_queue, args=(solver_queue_name, identifier,)).start()
        


    def post_to_solver_db(self, ch, body, identifier):
        ch.queue_declare(queue="db-queue")
        ch.basic_publish(exchange='', routing_key="db-queue", body=body)
        result_db_queue_name = f"result-db-queue-{identifier}"
        ch.queue_declare(queue="db-queue")
        print("ASDASDASD:", body , flush=True)
        ch.basic_publish(exchange='', routing_key="db-queue", body=body)
        print(f"Calling async c_f_db_r_q: ({result_db_queue_name})..", flush=True)
        threading.Thread(target=self.consume_from_db_result_queue, args=(result_db_queue_name, identifier,)).start()