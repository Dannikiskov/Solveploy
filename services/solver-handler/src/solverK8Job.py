from kubernetes import client, config
import uuid

def start_solver_job(identifier):
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create a unique job name
    job_name = f"solver-job-{identifier}.id"

    # Create solver job
    solver_job = create_solver_job(job_name, str(identifier))
    batch_api = client.BatchV1Api()

    batch_api.create_namespaced_job(namespace="default", body=solver_job)
    return job_name

def create_solver_job(job_name, identifier):
    return client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="solver-container",
                            image="solver-pod:latest",
                            image_pull_policy="Never",
                            env=[
                                client.V1EnvVar(
                                    name="IDENTIFIER",
                                    value=identifier,
                                ),
                                client.V1EnvVar(
                                    name="RABBITMQ_USERNAME",
                                    value_from=client.V1EnvVarSource(
                                        secret_key_ref=client.V1SecretKeySelector(
                                            name="message-broker-default-user",
                                            key="username",
                                        )
                                    ),
                                ),
                                client.V1EnvVar(
                                    name="RABBITMQ_PASSWORD",
                                    value_from=client.V1EnvVarSource(
                                        secret_key_ref=client.V1SecretKeySelector(
                                            name="message-broker-default-user",
                                            key="password",
                                        )
                                    ),
                                ),
                            ],
                        )
                    ],
                    restart_policy="Never",
                    active_deadline_seconds=1800,
                )
            ),
            ttl_seconds_after_finished=20,
        )
    )


def stop_solver_job(identifier):
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create Kubernetes API client
    batch_api = client.BatchV1Api()
    core_api = client.CoreV1Api()

    # Get all pods in the default namespace
    jobs = batch_api.list_namespaced_job(namespace="default")

    # Iterate over the pods and delete the one with the specified job name
    for job in jobs.items:
        print("Looking at: ", job.metadata.name, flush=True)
        if f"solver-job-{identifier}.id" in job.metadata.name:
            print("Deleting: ", job.metadata.name, flush=True)
            batch_api.delete_namespaced_job(name=job.metadata.name, namespace="default")
            break
    
    # Get all pods in the default namespace
    pods = core_api.list_namespaced_pod(namespace="default")

    # Iterate over the pods and delete the one with the specified job name
    for pod in pods.items:
        print("Looking at: ", pod.metadata.name, flush=True)
        if f"solver-job-{identifier}.id" in pod.metadata.name:
            print("Deleting: ", pod.metadata.name, flush=True)
            core_api.delete_namespaced_pod(name=pod.metadata.name, namespace="default")
            break
    
    
