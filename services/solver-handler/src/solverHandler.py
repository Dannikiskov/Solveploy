import json
import messageQueue as mq
import solverK8Job
import minizinc
from pathlib import Path
import uuid

def solver_handler(data):
    print("Solver Handler:::", data, flush=True)
    json_data = json.dumps(data)
    solverK8Job.start_solver_job(data["identifier"])
    result = mq.send_wait_receive_k8(data, f'solverk8job-{data["identifier"]}')
    mq.send_to_queue(result, f'{data["queue_name"]}-{data["identifier"]}')



def start_solver(data):

    identifier = data["item"]["solverIdentifier"]

    solverK8Job.start_solver_job(identifier)
    result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')
    dict = {"mznFileContent": data["mznFileContent"], "executionTime": data["executionTime"] ,"instructions": "HandleInstance", "queue_name": "knowledge-base"}
    mq.send_to_queue(json.dumps(dict), "knowledge-base")
    json_result = json.loads(result)
    mq.send_to_queue(json_result, f'{data["queue_name"]}-{identifier}')

def stop_solver(data):

    identifier = data["item"]["solverIdentifier"]

    print("Stop Solver:::", data, flush=True)
    solverK8Job.stop_solver_job(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queue_name"]}-{identifier}')


def get_solvers(data):
    path = Path("/app/MiniZincIDE-2.8.2-bundle-linux-x86_64/bin/minizinc")
    mzn_driver = minizinc.Driver(path)
    solvers = mzn_driver.available_solvers()
    
    available_solvers = []
    for index, (solver_name, solver_list) in enumerate(solvers.items()):
        if "." not in solver_name:
            available_solvers.append({"name": solver_name, "mzn_identifier": solver_list[0].id})
    
    mq.send_to_queue(available_solvers, f'{data["queue_name"]}-{data["identifier"]}')