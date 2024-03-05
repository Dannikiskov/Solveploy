
import messageQueue as mq
import uuid

def get_all_feature_vectors(identifier):
    data = create_dict(identifier)
    mq.send_wait_receive(data)


def handle_instance(file_data):
    data = create_dict('HandleInstance', file_data)
    mq.send_wait_receive(data)


def get_solved(solvers, similar_insts, T):
    data = create_dict('GetSolved', {'solvers': solvers, 'similarInsts': similar_insts, 'T': T})
    mq.send_wait_receive(data)


def get_solved_times(solver_id, similar_insts):
    data = create_dict('GetSolvedTimes', {'solverId': solver_id, 'similarInsts': similar_insts})
    mq.send_wait_receive(data)

def get_solvers():
    data = create_dict('GetSolvers')
    mq.send_wait_receive(data)

def create_dict(instructions, content=None):
    return {'identifier': str(uuid.uuid4()), 'queueName': "kbHandler", 'instructions': instructions, 'content': content}
    
