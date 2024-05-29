import messageQueue as mq
import k8sHandler
from pathlib import Path
import tempfile
import sat_feat_py.generate_features as gf

def handle_new_sat_job(data):

    identifier = data["item"]["jobIdentifier"]
    solver_name = data["item"]["name"]
    cpu = data["item"]["cpu"]
    memory = data["item"]["memory"]

    k8sHandler.start_solver_job(solver_name, identifier, "sat", cpu, memory)
    k8s_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')

    print(f"{solver_name}: {k8s_result['status']}: {data["satFileName"]}")
    # Get feature vector
    if k8s_result["status"] not in ["ERROR", "FAILED"]:
        feature_vector = gf.generate_features(data["satFileContent"])
        print(f"Feature vector: {feature_vector}", flush=True)
        dict = {"satFileName": data["satFileName"],
                "featureVector": feature_vector,
                "solverName": solver_name,
                "executionTime": k8s_result["executionTime"], 
                "status": k8s_result["status"], 
                "instructions": "HandleSatInstance", 
                 "queueName": "kbHandler"}
        mq.send_to_queue(dict, "kbHandler")


    mq.send_to_queue(k8s_result, f'{data["queueName"]}-{identifier}')


def stop_sat_job_by_id(data):

    identifier = data["item"]["jobIdentifier"]

    k8sHandler.stop_solver_job_by_id(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queueName"]}-{identifier}')



def get_available_sat_solvers(data):

    available_solvers = [
        ('cd15', 'cd153', 'cdl15', 'cdl153', 'cadical153'),
        ('cms', 'cms5', 'crypto', 'crypto5', 'cryptominisat', 'cryptominisat5'),
        ('gc3', 'gc30', 'gluecard3', 'gluecard30'),
        ('gsu', 'gimsatul'),
        ('g42', 'g421', 'glucose42', 'glucose421'),
        ('lgl', 'lingeling'),
        ('mcb', 'chrono', 'maplechrono'),
        ('mpl', 'maple', 'maplesat'),
        ('mg3', 'mgs3', 'mergesat3', 'mergesat30'),
        ('m22', 'msat22', 'minisat22'),
    ]

    solvers_dict = [{"name": solver[-1], "satIdentifier": solver[0]} for solver in available_solvers]

    mq.send_to_queue(solvers_dict, f'{data["queueName"]}-{data["identifier"]}')