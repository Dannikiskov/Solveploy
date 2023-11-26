#!/usr/bin/env python
import os
import pika

def sendHelloWorld():
  rabbitmq_username = os.getenv("RABBITMQ_USERNAME")
  rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
  print(rabbitmq_username, flush=True)
  print(rabbitmq_password, flush=True)
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='message-broker.default.svc.cluster.local', credentials=pika.PlainCredentials(rabbitmq_username, rabbitmq_password)))
  channel = connection.channel()

  channel.queue_declare(queue='hello')

  channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
  print(" [x] Sent 'Hello World!'", flush=True)
  connection.close()