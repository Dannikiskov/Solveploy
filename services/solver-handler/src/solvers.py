from kubernetes import client, config
import uuid

def start_solver_job(identifier):
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create a unique job name
    job_name = f"solver-job-{identifier}"

    # Create solver job
    solver_job = create_solver_job(job_name, identifier)
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job(namespace="default", body=solver_job)
    print("JOB NAME:", job_name, flush=True)
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
                                    name="JOB_NAME",
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
                )
            ),
            ttl_seconds_after_finished=15,
        )
    )
