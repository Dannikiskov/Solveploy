import messageQueue as mq
import k8sHandler
import minizinc
from pathlib import Path
import tempfile
import subprocess


def handle_new_mzn_job(data):
    dznIncluded = False
    identifier = data["item"]["jobIdentifier"]
    solver_name = data["item"]["name"]
    cpu = data["item"]["cpu"]
    memory = data["item"]["memory"]
    data_type = data["dataFileType"]
    k8sHandler.start_solver_job(solver_name, identifier, "mzn", cpu, memory)
    k8_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')


    temp_file_mzn = tempfile.NamedTemporaryFile(suffix=".mzn", delete=False)
    temp_file_mzn.write(data['mznFileContent'].encode())
    temp_file_mzn.close()

    if data['dataFileContent'] is not None and data['dataFileContent'] != "":
        temp_file_dzn = tempfile.NamedTemporaryFile(suffix=data_type, delete=False)
        temp_file_dzn.write(data['dataFileContent'].encode())
        temp_file_dzn.close()
        dznIncluded = True


    # Get feature vector
    if dznIncluded:
        command = ["mzn2feat", "-i", temp_file_mzn.name, "-d", temp_file_dzn.name]
    else:
        command = ["mzn2feat", "-i", temp_file_mzn.name]

    cmd_result = subprocess.run(command, capture_output=True, text=True)
    
    feature_vector = cmd_result.stdout.strip()
    feature_vector = feature_vector.split(',')
    feature_vector = [str(float(i)) if 'e' in i else i for i in feature_vector]
    feature_vector = ','.join(feature_vector)
    # print("\n\n\nFeature vector: ", feature_vector, "\n\n\n", flush=True)
    
    if "executionTime" in k8_result and k8_result["executionTime"] != "N/A":
        dict = {"optVal": data["optVal"], "featureVector": feature_vector, "solverName": solver_name, "executionTime": k8_result["executionTime"], "result": k8_result["result"], "instructions": "HandleMznInstance", "queueName": "kbHandler"}
        mq.send_to_queue(dict, "kbHandler")

    mq.send_to_queue(k8_result, f'{data["queueName"]}-{identifier}')


def stop_mzn_job_by_id(data):

    identifier = data["item"]["jobIdentifier"]

    k8sHandler.stop_solver_job(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queueName"]}-{identifier}')

def get_available_mzn_solvers(data):
    path = Path("/app/MiniZincIDE-2.8.2-bundle-linux-x86_64/bin/minizinc")
    mzn_driver = minizinc.Driver(path)
    solvers = mzn_driver.available_solvers()

    available_solvers = []
    for solver in solvers.keys():
        if solver.__contains__("."):
            solver_name = solver.split(".")[-1]
            available_solvers.append({"name": solver_name, "version": solvers[solver_name][0].version})
    
    mq.send_to_queue(available_solvers, f'{data["queueName"]}-{data["identifier"]}')