import messageQueue as mq
import solverK8Job
from pathlib import Path
import tempfile
import sat_feat_py.generate_features as gf
import pysat.solvers

def handle_new_sat_job(data):

    identifier = data["item"]["jobIdentifier"]
    solver_name = data["item"]["name"]

    solverK8Job.start_solver_job(solver_name, identifier, "sat")
    k8_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')
    
    # Get feature vector
    try:
        feature_vector = gf.generate_features(data["cnfFileContent"])
        dict = {"featureVector": feature_vector, "solverName": solver_name, "executionTime": k8_result["executionTime"], "instructions": "HandleSatInstance", "queueName": "kbHandler"}
        mq.send_to_queue(dict, "kbHandler")
    except Exception as e:
        print(f"Exception occurred: {str(e)}", flush=True)


    
    mq.send_to_queue(k8_result, f'{data["queueName"]}-{identifier}')


def stop_sat_job(data):

    identifier = data["item"]["jobIdentifier"]

    solverK8Job.stop_solver_job(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queueName"]}-{identifier}')


def get_available_sat_solvers(data):

    available_solvers = [
        ('cd', 'cd103', 'cdl', 'cdl103', 'cadical103'),
        ('cd15', 'cd153', 'cdl15', 'cdl153', 'cadical153'),
        ('cms', 'cms5', 'crypto', 'crypto5', 'cryptominisat', 'cryptominisat5'),
        ('gc3', 'gc30', 'gluecard3', 'gluecard30'),
        ('gc4', 'gc41', 'gluecard4', 'gluecard41'),
        ('g3', 'g30', 'glucose3', 'glucose30'),
        ('g4', 'g41', 'glucose4', 'glucose41'),
        ('g42', 'g421', 'glucose42', 'glucose421'),
        ('lgl', 'lingeling'),
        ('mcb', 'chrono', 'maplechrono'),
        ('mcm', 'maplecm'),
        ('mpl', 'maple', 'maplesat'),
        ('mg3', 'mgs3', 'mergesat3', 'mergesat30'),
        ('mc', 'mcard', 'minicard'),
        ('m22', 'msat22', 'minisat22'),
        ('mgh', 'msat-gh', 'minisat-gh')
    ]

    solvers_dict = [{"name": solver[-1], "satIdentifier": solver[0]} for solver in available_solvers]

    mq.send_to_queue(solvers_dict, f'{data["queueName"]}-{data["identifier"]}')