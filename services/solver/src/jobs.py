# main_script.py

import os
from kubernetes import client, config
import time

id = 0
def start_minizinc_job(model_string, solver_name="gecode"):
    global id
    id = id + 1
    print("------------------PRINTING ID:", id, " --------------")
    # Set environment variables
    os.environ["MODEL_STRING"] = model_string
    os.environ["SOLVER_NAME"] = solver_name

    # Load Kubernetes configuration
    config.load_incluster_config()
    jobname= f"minizinc-job-%s" % id
    # Create a Kubernetes Job object
    job = client.V1Job(
    metadata=client.V1ObjectMeta(name=jobname),
    spec=client.V1JobSpec(
        template=client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                service_account_name="default",  # Ensure this is set to "default"
                containers=[
                    client.V1Container(
                        name="minizinc-container",
                        image="minizinc-job-image",
                        env=[
                            client.V1EnvVar(name="MODEL_STRING", value=os.environ["MODEL_STRING"]),
                            client.V1EnvVar(name="SOLVER_NAME", value=os.environ["SOLVER_NAME"]),
                        ],
                    )
                ],
                restart_policy="Never",
            )
        )
    )
)


    # Create the Job in the cluster
    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job(namespace="default", body=job)

    while True:
        print("TRYING JOB STATUS...")
        job_status = batch_api.read_namespaced_job_status(name=jobname, namespace="default")
        if job_status.status.succeeded:
            print("Job completed successfully.")
            break
        elif job_status.status.failed:
            print("Job failed.")
            break
        else:
            print("Waiting for the Job to complete...")
            time.sleep(2)

    # Get the name of the Pod associated with the Job
    pod_name = job_status.spec.selector.match_labels['controller-uid']

    # Retrieve the logs of the Pod
    pod_logs = batch_api.read_namespaced_pod_log(name=pod_name, namespace="default")
    print("Pod Logs:", pod_logs)

    result_start_marker = "=== RESULT START ==="
    result_end_marker = "=== RESULT END ==="

    result_start_index = pod_logs.find(result_start_marker)
    result_end_index = pod_logs.find(result_end_marker)

    if result_start_index != -1 and result_end_index != -1:
        result_section = pod_logs[result_start_index + len(result_start_marker):result_end_index]
    print("Extracted Result:", result_section.strip())
