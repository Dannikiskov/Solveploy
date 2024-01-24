
import messageQueue
import uuid

def get_all_feature_vectors(identifier):
    data = create_dict(identifier)
    messageQueue.send_wait_receive(data)


def handle_instance(file_data):
    data = create_dict('HandleInstance', file_data)
    messageQueue.send_wait_receive(data)


def get_solved(solvers, similar_insts, T):
    data = create_dict('GetSolved', {'solvers': solvers, 'similar_insts': similar_insts, 'T': T})
    messageQueue.send_wait_receive(data)


def get_solved_times(solver_id, similar_insts):
    data = create_dict('GetSolvedTimes', {'solver_id': solver_id, 'similar_insts': similar_insts})
    messageQueue.send_wait_receive(data)

def get_solvers():
    data = create_dict('GetSolvers')
    messageQueue.send_wait_receive(data)

def create_dict(instructions, content=None):
    return {'identifier': str(uuid.uuid4()), 'queue_name': "knowledge-base", 'instructions': instructions, 'content': content}
    
