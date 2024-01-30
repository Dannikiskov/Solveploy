import json
import subprocess
import numpy as np
import kb
import messageQueue
import solverK8Job
import minizinc
from pathlib import Path

def solver_handler(data):
    print("Solver Handler:::", data, flush=True)
    json_data = json.dumps(data)
    solverK8Job.start_solver_job(data["identifier"])
    result = messageQueue.send_wait_receive_k8(data, f'solverk8job-{data["identifier"]}')
    messageQueue.send_to_queue(result, f'{data["queue_name"]}-{data["identifier"]}')



def start_solver(data):

    print("Name: ", data["selectedItem"]["name"], flush=True)
    print("ID: ", data["selectedItem"]["id"], flush=True)
    print("MZN: ", data["mznFileContent"], flush=True)

    solverK8Job.start_solver_job(data["identifier"])
    result = messageQueue.send_wait_receive_k8(data, f'solverk8job-{data["identifier"]}')
    json_result = json.loads(result)
    messageQueue.send_to_queue(json_result, f'{data["queue_name"]}-{data["identifier"]}')


def get_solvers(data):
    path = Path("/app/MiniZincIDE-2.8.2-bundle-linux-x86_64/bin/minizinc")
    mzn_driver = minizinc.Driver(path)
    solvers = mzn_driver.available_solvers()
    
    available_solvers = []
    for solver_name, solver_list in solvers.items():
        if "." not in solver_name:
            available_solvers.append({"name": solver_name, "id": solver_list[0].id})
    
    messageQueue.send_to_queue(available_solvers, f'{data["queue_name"]}-{data["identifier"]}')