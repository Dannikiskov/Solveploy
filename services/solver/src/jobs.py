import os
import tempfile
from kubernetes import client, config
import time
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_minizinc_job(model_string, namespace="default"):
    try:
        # Load Kubernetes configuration
        config.load_incluster_config()

        # Create a unique job name
        job_name = f"minizinc-job-{int(time.time())}-{str(uuid.uuid4())[:8]}"

        logger.info(f"Starting Minizinc job with name: {job_name}")

        # Get the current working directory
        current_directory = os.path.dirname(__file__)

        # Create a temporary file with the Minizinc model content in the current directory
        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".mzn", dir=current_directory)
        temp_file.write(model_string)
        temp_model_path = temp_file.name

        try:
            # Create Minizinc job
            minizinc_job = create_minizinc_job(job_name, temp_model_path)
            batch_api = client.BatchV1Api()
            batch_api.create_namespaced_job(namespace=namespace, body=minizinc_job)

            # Wait for the Minizinc job to complete
            wait_for_job_completion(batch_api, job_name, namespace)
        finally:
            # Cleanup: Remove the temporary model file
            os.remove(temp_model_path)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

def create_minizinc_job(job_name, model_path):
    return client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="minizinc-container",
                            image="minizinc/minizinc:latest",
                            command=["minizinc"],
                            args=[
                                "--help"
                            ],
                        )
                    ],
                    restart_policy="OnFailure",
                )
            )
        )
    )

def wait_for_job_completion(api, job_name, namespace):
    while True:
        logger.info(f"Checking status for Minizinc job: {job_name}")
        job_status = api.read_namespaced_job_status(name=job_name, namespace=namespace)
        if job_status.status.succeeded:
            logger.info("Minizinc job completed successfully.")
            break
        elif job_status.status.failed:
            logger.error("Minizinc job failed.")
            break
        else:
            logger.info("Waiting for the Minizinc job to complete...")
            time.sleep(2)

