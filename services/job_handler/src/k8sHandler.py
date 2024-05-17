import base64
import uuid
from kubernetes import client, config

import os
import messageQueue as mq

def start_solver_job(solver_name, identifier, image_prefix, cpu, memory):
    global i
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create a unique job name
    job_name = f"{solver_name.lower()}-{identifier}"
    print("Job name: ", job_name, flush=True)

    config.load_incluster_config()

    v1 = client.CoreV1Api()

    # Get the secret
    secret = v1.read_namespaced_secret("rabbitmq", "default")

    # Decode the secret data
    password = base64.b64decode(secret.data['rabbitmq-password']).decode()

    cpu = str(cpu) + "m"
    memory = str(memory) + "Mi"

    # Create solver job
    solver_job = create_solver_job(job_name, str(identifier), image_prefix, cpu, memory, 'user', password)
    batch_api = client.BatchV1Api()

    batch_api.create_namespaced_job(namespace=image_prefix, body=solver_job)

    return job_name

def create_solver_job(job_name, identifier, image_prefix, cpu_request, memory_request, username, password):
    return client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=f"{image_prefix}-container",
                            image=f"{image_prefix}-pod:latest",
                            image_pull_policy="Never",
                            env=[
                                client.V1EnvVar(
                                    name="IDENTIFIER",
                                    value=identifier,
                                ),
                                client.V1EnvVar(
                                    name="RABBITMQ_USERNAME",
                                    value=username,
                                ),
                                client.V1EnvVar(
                                    name="RABBITMQ_PASSWORD",
                                    value=password,
                                ),
                            ],
                            resources=client.V1ResourceRequirements(
                                requests={
                                    "cpu": cpu_request,
                                    "memory": memory_request
                                }
                            )
                        )
                    ],
                    restart_policy="Never",
                )
            ),
            ttl_seconds_after_finished=150,
        )
    )


def stop_namespaced_jobs(namespace):
    
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create Kubernetes API client
    batch_api = client.BatchV1Api()
    core_api = client.CoreV1Api()

    # Get all pods in the default namespace
    jobs = batch_api.list_namespaced_job(namespace=namespace)

    # Iterate over the pods and delete the one with the specified job name
    for job in jobs.items:
        print("Deleting: ", job.metadata.name, flush=True)
        batch_api.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
    
    # Get all pods in the default namespace
    pods = core_api.list_namespaced_pod(namespace=namespace)

    # Iterate over the pods and delete the one with the specified job name
    for pod in pods.items:
        print("Deleting: ", pod.metadata.name, flush=True)
        core_api.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
    
def stop_specific_job(namespace, identifier):
    # Load Kubernetes configuration
    config.load_incluster_config()
    print("Namespace: ", namespace, flush=True)
    print("Identifier: ", identifier, flush=True)
    # Create Kubernetes API client
    batch_api = client.BatchV1Api()
    core_api = client.CoreV1Api()

    # Get all pods in the default namespace
    jobs = batch_api.list_namespaced_job(namespace=namespace)

    # Iterate over the pods and delete the one with the specified job name
    for job in jobs.items:
        print("Looking at: ", job.metadata.name, flush=True)
        if identifier in job.metadata.name:
            print("Deleting: ", job.metadata.name, flush=True)
            batch_api.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
            break
    
    # Get all pods in the default namespace
    pods = core_api.list_namespaced_pod(namespace=namespace)

    # Iterate over the pods and delete the one with the specified job name
    for pod in pods.items:
        print("Looking at: ", pod.metadata.name, flush=True)
        if identifier in pod.metadata.name:
            print("Deleting: ", pod.metadata.name, flush=True)
            core_api.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
            break