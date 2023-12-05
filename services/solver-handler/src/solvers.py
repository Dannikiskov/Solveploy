from kubernetes import client, config
import uuid

def start_solver_job(model):
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Convert bytes to string
    model = model.decode('utf-8')

    # Create a unique job name
    job_name = f"minizinc-job-{str(uuid.uuid4())[:8]}"

    # Create Minizinc job
    minizinc_job = create_minizinc_job(job_name)
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job(namespace="default", body=minizinc_job)
    print("JOB NAME:", job_name, flush=True)
    return job_name

def create_minizinc_job(job_name):
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
                                    name="JOB_NAME",
                                    value=job_name,
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
                )
            )
        )
    )
