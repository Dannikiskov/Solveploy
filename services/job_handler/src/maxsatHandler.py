import messageQueue as mq
import solverK8Job
import sat_feat_py.generate_features as gf


def handle_new_maxsat_job(data):

    identifier = data["item"]["jobIdentifier"]
    solver_name = data["item"]["name"]

    solverK8Job.start_solver_job(solver_name, identifier, "maxsat")
    k8_result = mq.send_wait_receive_k8(data, f'solverk8job-{identifier}')
    
    # Get feature vector and sent to kb
    try:
        feature_vector = gf.generate_features(data["cnfFileContent"])
        dict = {"featureVector": feature_vector, "solverName": solver_name, "executionTime": k8_result["executionTime"], "instructions": "HandleMaxsatInstance", "queueName": "kbHandler"}
        mq.send_to_queue(dict, "kbHandler")
    except Exception as e:
        print(f"Exception occurred: {str(e)}", flush=True)


    
    mq.send_to_queue(k8_result, f'{data["queueName"]}-{identifier}')


def stop_maxsat_job(data):

    identifier = data["item"]["jobIdentifier"]

    solverK8Job.stop_solver_job(identifier)
    mq.send_to_queue("Solver stopped", f'{data["queueName"]}-{identifier}')


def get_available_maxsat_solvers(data):

    available_solvers = ['RC2']

    solvers_dict = [{"name": solver, "maxsatIdentifier": solver} for solver in available_solvers]

    mq.send_to_queue(solvers_dict, f'{data["queueName"]}-{data["identifier"]}')