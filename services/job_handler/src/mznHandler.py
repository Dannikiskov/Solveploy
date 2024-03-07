import messageQueue as mq
import solverK8Job
import minizinc
from pathlib import Path
import tempfile
import subprocess

def handle_new_mzn_job(data):

    identifier = data["item"]["solverIdentifier"]
    solver_name = data["item"]["name"]

    solverK8Job.start_solver_job(solver_name, identifier, "mzn")
    k8_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')

    temp_file = tempfile.NamedTemporaryFile(suffix=".mzn", delete=False)
    temp_file.write(data['mznFileContent'].encode())
    
    # Get feature vector
    command = ["mzn2feat", "-i", temp_file.name]
    cmd_result = subprocess.run(command, capture_output=True, text=True)
    feature_vector = cmd_result.stdout.strip()
    temp_file.close()

    dict = {"featureVector": feature_vector, "solverName": solver_name, "executionTime": k8_result["executionTime"], "instructions": "HandleMznInstance", "queueName": "kbHandler"}
    mq.send_to_queue(dict, "kbHandler")
    mq.send_to_queue(k8_result, f'{data["queueName"]}-{identifier}')


def stop_job(data):

    identifier = data["item"]["solverIdentifier"]

    solverK8Job.stop_solver_job(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queueName"]}-{identifier}')


def get_available_mzn_solvers(data):
    path = Path("/app/MiniZincIDE-2.8.2-bundle-linux-x86_64/bin/minizinc")
    mzn_driver = minizinc.Driver(path)
    solvers = mzn_driver.available_solvers()
    
    available_solvers = []
    for index, (solver_name, solver_list) in enumerate(solvers.items()):
        if "." not in solver_name:
            available_solvers.append({"name": solver_name, "mznIdentifier": solver_list[0].id})
    
    mq.send_to_queue(available_solvers, f'{data["queueName"]}-{data["identifier"]}')