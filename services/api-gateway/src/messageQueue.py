import pika
import os
import uuid
import json
import threading
import time

class MessageQueue:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='message-broker.default.svc.cluster.local', 
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USERNAME"), os.getenv("RABBITMQ_PASSWORD"))))
        
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='direct-exchange', exchange_type='direct')
        self.channel.exchange_declare(exchange='direct-exchange2', exchange_type='direct')
        self.channel.queue_declare(queue='job-queue')
        self.channel.queue_declare(queue='result-queue')

        # Create a result queue for each job in a dictionary
        self.result_queues = {}
        self.jobs = {}  # Initialize self.jobs

        # Start the message consumption thread
        self.consumer_thread = threading.Thread(target=self.consume_messages, daemon=True)
        self.consumer_thread.start()

    def consume_messages(self):
        while True:
            try:
                result_queue_name = "result-queue"
                self.channel.queue_bind(exchange='direct-exchange',  
                                        queue=result_queue_name,
                                        routing_key='job-queue')

                print(f" [*] Waiting for result in '{result_queue_name}'", flush=True)

                def callback(ch, method, properties, body):
                    try:
                        print(f" [x] Received result: {body}", flush=True)
                        job_id = json.loads(body)['job_id']
                        self.jobs[job_id] = body
                        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message
                    except Exception as e:
                        print(f"Error in callback: {e}")

                self.channel.basic_consume(queue=result_queue_name,
                                        on_message_callback=callback,
                                        auto_ack=False)  # Set auto_ack to False

                # Start consuming messages in a separate thread
                consume_thread = threading.Thread(target=self.channel.start_consuming)
                consume_thread.start()
                consume_thread.join()  # Wait for the thread to finish (this is usually done in the main application loop)
            except Exception as e:
                print(f"Error in consume_messages: {e}")
                time.sleep(1)  # Sleep before attempting to reconnect
    def sendJob(self, data):
        job_id = str(uuid.uuid4())
        job_queue_name = "job-queue"

        message_data = {
            'job_id': job_id,
            'data': data,
        }

        message_body = json.dumps(message_data)

        self.channel.basic_publish(
            exchange='direct-exchange2',
            routing_key=job_queue_name,
            body=message_body
        )

        print(f" [x] Sent job to '{job_queue_name}' for job ID: {job_id}", flush=True)
        return job_id

    def waitForResult(self, job_id):
        self.result_queues[job_id] = None  # Initialize result_queues
        while self.result_queues[job_id] is None:
            time.sleep(0.1)  # Adjust the sleep duration based on your requirements

        result = self.result_queues[job_id]
        self.result_queues[job_id] = None  # Reset the result for the next job
        return result

    def close_connection(self):
        self.connection.close()

# Example usage:
# mq = MessageQueue()
# mq.sendJob("testdata")
# result = mq.waitForResult(job_id)
# mq.close_connection()
