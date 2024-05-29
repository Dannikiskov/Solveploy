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
    

    k8s_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')

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
    
    if k8s_result["status"] not in ["ERROR", "FAILED"]:
        dict = {"dataFileName": data["dataFileName"],
                "mznFileName": data["mznFileName"],
                "optGoal": data["optGoal"], 
                "optVal": k8s_result["optVal"], 
                "featureVector": feature_vector, "solverName": solver_name,
                "executionTime": k8s_result["executionTime"], 
                "status": k8s_result["status"], 
                "result": k8s_result["result"], 
                "instructions": "HandleMznInstance",
                "queueName": "kbHandler"}
        print("LOOOCK HERERERER:", flush=True)
        print(dict["optVal"], flush=True)
        mq.send_to_queue(dict, "kbHandler")

    mq.send_to_queue(k8s_result, f'{data["queueName"]}-{identifier}')


def get_available_mzn_solvers(data):
    available_solvers = [{"name": "gecode"}, {'name': 'chuffed'}, {'name': 'coin-bc'}, {'name': 'highs'}, {'name': 'or tools cp-sat'}]
    mq.send_to_queue(available_solvers, f'{data["queueName"]}-{data["identifier"]}')