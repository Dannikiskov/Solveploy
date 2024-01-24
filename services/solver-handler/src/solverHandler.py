import json
import subprocess
import numpy as np
import kb
import messageQueue
import solverK8Job

def solver_handler(data):
    print("Solver Handler:::", data, flush=True)
    json_data = json.dumps(data)
    solverK8Job.start_solver_job(data["identifier"])
    result = messageQueue.send_wait_receive_k8(data, f'solverk8job-{data["identifier"]}')
    messageQueue.send_to_queue(result, f'{data["queue_name"]}-{data["identifier"]}')