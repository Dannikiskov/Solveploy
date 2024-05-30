from itertools import chain, combinations
import subprocess
import tempfile
import numpy as np
import kb
import messageQueue as mq
import ast
import sat_feat_py.generate_features as gf
from collections import defaultdict



def sunny(inst, solvers, bkup_solver, k, T, identifier, solver_type, data_file=None, data_type=None):
    solvers = [solver['name'] for solver in solvers]

    # Get features vector for the given instance
    feat_vect = get_features(inst, solver_type, data_file, data_type)

    # Find k-nearest neighbors
    similar_insts = get_nearest_neighbors(feat_vect, k, solver_type)

    # Get sub-portfolio
    sub_portfolio, matrix = get_sub_portfolio(similar_insts, solvers, T, solver_type)

    # Initialize variables
    slots = sum([get_max_solved(solver, matrix, T) for solver in sub_portfolio]) + (k - get_max_solved(sub_portfolio, matrix, T))
    time_slot = T / slots
    tot_time = 0
    schedule = {bkup_solver['name']: 0}

    # Populate the schedule
    for solver in sub_portfolio:
        solver_slots = get_max_solved(solver, matrix, T)
        schedule[solver] = solver_slots * time_slot
        tot_time += solver_slots * time_slot

    # Adjust backup solver time
    if tot_time < T:
        schedule[bkup_solver['name']] += T - tot_time

    # Return sorted schedule
    result = sorted(schedule.items(), key=lambda x: x[1]).reverse()
    result = dict(result)

    mq.send_to_queue({"result": result}, f"jobHandler-{identifier}")


def get_features(inst, solver_type, data_file, data_type):
    if solver_type == "mzn":
        temp_file_mzn = tempfile.NamedTemporaryFile(suffix=".mzn", delete=False)
        temp_file_mzn.write(inst.encode())
        temp_file_mzn.close()

        if data_file is not None and data_file != "":
            temp_file_dzn = tempfile.NamedTemporaryFile(suffix=data_type, delete=False)
            temp_file_dzn.write(data_file.encode())
            temp_file_dzn.close()
            dznIncluded = True

        if dznIncluded:
            command = ["mzn2feat", "-i", temp_file_mzn.name, "-d", temp_file_dzn.name]
        else:
            command = ["mzn2feat", "-i", temp_file_mzn.name]


        cmd_result = subprocess.run(command, capture_output=True, text=True)
        
        feature_vector = cmd_result.stdout.strip()
        feature_vector = feature_vector.split(',')
        feature_vector = [str(float(i)) if 'e' in i else i for i in feature_vector]
        feature_vector = ','.join(feature_vector)

        return feature_vector

    if solver_type == "sat" or solver_type == "maxsat":
        feature_vector_dict = gf.generate_features(inst)
        feature_vector = ",".join(str(x) for x in feature_vector_dict.values())
        return feature_vector
        
       

def get_nearest_neighbors(feat_vect, k, solver_type):
    feat_vect = [float(i) for i in feat_vect.split(',')]

    kb_features = kb.get_all_feature_vectors(solver_type)
    if kb_features == None:
        return feat_vect
    
    kb_features = ast.literal_eval(kb_features)

    if len(kb_features) >= k:
        distances = [euclidean_distance(feat_vect, kb_feature) for kb_feature in kb_features]
    else:  
        return kb_features

    nearest_indices = np.argsort(distances)[:k]
    nearest_neighbors = [kb_features[i] for i in nearest_indices]

    return nearest_neighbors


def get_sub_portfolio(similar_insts, solvers, T, solver_type):

    # Generate all possible subsets of solvers
    subsets = []
    for r in range(1, len(solvers)):
        subsets.extend(combinations(solvers, r))
    
    data_str = kb.matrix(solvers, similar_insts, T, solver_type)
    data = ast.literal_eval(data_str)
    print("\n", data, "\n", flush=True)

    distinct_numbers = len(set(item[1] for item in data))

    # Create a dictionary where each key is a solver and the value is a list of the times it took to solve the problems
    solver_to_times = {}
    for solver, problem, time in data:
        if time != "T":
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(float(time))

    # Create all subsets of solvers
    subsets = list(chain.from_iterable(combinations(solvers, r) for r in range(1, len(solvers))))

    # Create a dictionary where each key is a solver and the value is a list of the instances it solved
    solver_to_instances = {}
    for solver, instance, time in data:
        if time != "T":
            if solver not in solver_to_instances:
                solver_to_instances[solver] = []
            solver_to_instances[solver].append(instance)

    # For each subset, calculate the total solve time, the average solve time, and find the subset with total time <= 1800 and the maximum number of unique solved instances
    max_solved_instances = 0
    min_time = float('inf')
    best_subsets = {}
    for subset in subsets:
        total_time = 0
        solved_instances = set()
        total_subset_time = 0
        for solver in subset:
            if solver in solver_to_instances:
                total_time += sum(solver_to_times[solver])
                solved_instances.update(solver_to_instances[solver])
                total_subset_time += sum(solver_to_times[solver]) + T*(distinct_numbers-len(solver_to_instances[solver])) 
        count = len(solved_instances)
        print("\n", flush=True)
        print("subset: ", subset, flush=True)
        print("len(subset): ", len(subset), flush=True)
        print("distinct_numbers: ", distinct_numbers, flush=True)
        print("\n", flush=True)
        average_time = total_subset_time / (distinct_numbers*len(subset))
        if total_time <= T and count >= max_solved_instances:
            if count > max_solved_instances or (count == max_solved_instances and total_time < min_time):
                best_subsets.clear()
                best_subsets[subset] = (count, average_time)
                max_solved_instances = count
                min_time = total_time
            elif count == max_solved_instances and total_time == min_time:
                best_subsets[subset] = (count, average_time)
    
    return (list(next(iter(best_subsets))), data)


def get_max_solved(solvers, matrix, T):
    if not (isinstance(solvers, list)):
        solvers = [solvers]
        
    solved_instances = set()
    for solver, instance, time in matrix:
        if solver in solvers and time != "T" and float(time) <= T:
            solved_instances.add(instance)
    return len(solved_instances)

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

