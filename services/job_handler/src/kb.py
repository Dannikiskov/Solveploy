
import messageQueue as mq
import uuid

def get_all_feature_vectors(solver_type):
    if solver_type == "mzn":
        data = create_dict("GetAllMznFeatureVectors")
    elif solver_type == "sat":
        data = create_dict("GetAllSatFeatureVectors")
    elif solver_type == "maxsat":
        data = create_dict("GetAllMaxsatFeatureVectors")

    all_feature_vectors = mq.send_wait_receive(data)
    
    return all_feature_vectors


def handle_instance(file_data):
    data = create_dict('HandleInstance', file_data)
    mq.send_wait_receive(data)


def get_solved(solvers, similar_insts, T):
    data = create_dict('GetSolved', {'solvers': solvers, 'similarInsts': similar_insts, 'T': T})
    mq.send_wait_receive(data)

def is_instance_solved(instance, solver, solver_type):
    if solver_type == 'mzn':
        data = create_dict('isInstanceSolvedMzn', {'instance': instance, 'solver': solver})
    if solver_type == 'sat':
        data = create_dict('IsInstanceSolvedSat', {'instance': instance, 'solver': solver})
    if solver_type == 'maxsat':
        data = create_dict('IsInstanceSolvedMaxSat', {'instance': instance, 'solver': solver})

    result = mq.send_wait_receive(data)
    return result

def get_all_solved(solver_type):
    if solver_type == 'mzn':
        data = create_dict('GetAllSolvedMzn')
    if solver_type == 'sat':
        data = create_dict('GetAllSolvedSat')
    if solver_type == 'maxsat':
        data = create_dict('GetAllSolvedMaxSat')

    result = mq.send_wait_receive(data)
    return result


# def get_insts_times(similar_insts, solver_type):
#     if solver_type == 'mzn':
#         data = create_dict('GetInstsTimesMzn', {'similarInsts': similar_insts})
#     if solver_type == 'sat':
#         data = create_dict('GetInstsTimesSat', {'similarInsts': similar_insts})
#     if solver_type == 'maxsat':
#         data = create_dict('GetInstsTimesMaxSat', {'similarInsts': similar_insts})
#     result = mq.send_wait_receive(data)
#     return result

def get_solver_times(solver_name, similar_insts, solver_type):
    if solver_type == 'mzn':
        data = create_dict('GetSolvedTimesMzn', {'solverName': solver_name, 'similarInsts': similar_insts})
    if solver_type == 'sat':
        data = create_dict('GetSolvedTimesSat', {'solverName': solver_name})
    if solver_type == 'maxsat':
        data = create_dict('GetSolvedTimesMaxSat', {'solverName': solver_name})
    result = mq.send_wait_receive(data)
    return result

def get_solvers():
    data = create_dict('GetSolvers')
    mq.send_wait_receive(data)

def create_dict(instructions, content=None):
    return {'identifier': str(uuid.uuid4()), 'queueName': "kbHandler", 'instructions': instructions, 'content': content}
    
