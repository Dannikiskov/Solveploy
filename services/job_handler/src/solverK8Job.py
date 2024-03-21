from kubernetes import client, config
import uuid

def start_solver_job(solver_name, identifier, image_prefix):
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create a unique job name
    job_name = f"solver-{solver_name.lower()}-{image_prefix}-{identifier}"

    # Create solver job
    solver_job = create_solver_job(job_name, str(identifier), image_prefix)
    batch_api = client.BatchV1Api()

    batch_api.create_namespaced_job(namespace=image_prefix, body=solver_job)
    return job_name

def create_solver_job(job_name, identifier, image_prefix):
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
            ttl_seconds_after_finished=30,
        )
    )


def k8s_namespace_init():
    # Load Kubernetes configuration
    config.load_incluster_config()

    # Create Kubernetes API client
    core_api = client.CoreV1Api()
    
    core_api.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name="sat")))
    core_api.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name="mzn")))
    core_api.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name="maxsat")))

    # k8s secret with name "message-broker-default-user"
    secrets = core_api.list_namespaced_secret(namespace="default")
    secret_data = None
    for secret in secrets.items:
        if secret.metadata.name == "message-broker-default-user":
            secret_data = secret
            break
    
    # Create a namespaced secret
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name="message-broker-default-user"),
        data={
            "username": secret_data.data["username"],
            "password": secret_data.data["password"],
        }
    )

    # Check if the secret already exists in the "sat" namespace
    try:
        core_api.read_namespaced_secret(name="message-broker-default-user", namespace="sat")
    except client.rest.ApiException as e:
        if e.status == 404:
            core_api.create_namespaced_secret(namespace="sat", body=secret)
        else:
            print("Secret already exists in sat", flush=True)

    # Check if the secret already exists in the "mzn" namespace
    try:
        core_api.read_namespaced_secret(name="message-broker-default-user", namespace="mzn")
    except client.rest.ApiException as e:
        if e.status == 404:
            core_api.create_namespaced_secret(namespace="mzn", body=secret)
        else:
            print("Secret already exists in mzn", flush=True)

    # Check if the secret already exists in the "maxsat" namespace
    try:
        core_api.read_namespaced_secret(name="message-broker-default-user", namespace="maxsat")
    except client.rest.ApiException as e:
        if e.status == 404:
            core_api.create_namespaced_secret(namespace="maxsat", body=secret)
        else:
            print("Secret already exists maxsat", flush=True)

    

def stop_solver_job_by_id(identifier):
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
    

def stop_solver_by_namespace(namespace):
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
