from itertools import chain, combinations
import subprocess
import tempfile
import numpy as np
import kb
import messageQueue as mq
import ast
import sat_feat_py.generate_features as gf



def sunny(inst, solvers, bkup_solver, k, T, identifier, solver_type, data_file=None, data_type=None):
    # Get features vector for the given instance
    print("printing arguments", k, T, identifier, data_type, flush=True)
    print("\n\nGetting features vector for the given instance", flush=True)
    feat_vect = [1.0]#get_features(inst, solver_type, data_file, data_type)
    print("feat_vect: ", feat_vect, flush=True)
    print("type feat_vect: ", type(feat_vect), flush=True)

    # Find k-nearest neighbors
    print("Finding k-nearest neighbors", flush=True)
    similar_insts = get_nearest_neighbors(feat_vect, k, solver_type)
    print("similar_insts: ", similar_insts, flush=True)
    print("similar_insts type: ", type(similar_insts), flush=True)
    print("sim insts length", len(similar_insts), flush=True)

    # Get sub-portfolio
    print("Getting sub-portfolio", flush=True)
    sub_portfolio = get_sub_portfolio(similar_insts, solvers, T, solver_type)
    print("sub_portfolio", sub_portfolio, flush=True)

    # Initialize variables
    print("Initializing variables", flush=True)
    slots = sum([get_max_solved(solver, similar_insts, T, solver_type) for solver in sub_portfolio]) + (k - get_max_solved(sub_portfolio, similar_insts, T, solver_type))
    print("slots", slots, flush=True)
    time_slot = T / slots
    print("time_slot", time_slot, flush=True)
    tot_time = 0
    schedule = {bkup_solver["name"]: 0}

    # Populate the schedule
    print("Populating the schedule", flush=True)
    for solver in sub_portfolio:
        solver_slots = get_max_solved(solver, similar_insts, T, solver_type)
        schedule[solver["name"]] = solver_slots * time_slot
        tot_time += solver_slots * time_slot

    print("schedule", schedule, flush=True)
    # Adjust backup solver time
    print("Adjusting backup solver time", flush=True)
    if tot_time < T:
        schedule[bkup_solver["name"]] += T - tot_time

    # Return sorted schedule
    result = sorted(schedule.items(), key=lambda x: x[1])
    result = dict(result)
    print("Returning sorted schedule: ", result, flush=True)

    mq.send_to_queue({"result": result}, f"jobHandler-{identifier}")


def get_features(inst, solver_type, data_file, data_type):
    print("solver_tpye: ", solver_type, flush=True)
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
            print("\ndznIncluded\n", flush=True)
            command = ["mzn2feat", "-i", temp_file_mzn.name, "-d", temp_file_dzn.name]
        else:
            command = ["mzn2feat", "-i", temp_file_mzn.name]

        print("command: ", command, flush=True)
        cmd_result = subprocess.run(command, capture_output=True, text=True)
        
        feature_vector = cmd_result.stdout.strip()
        feature_vector = feature_vector.split(',')
        feature_vector = [str(float(i)) if 'e' in i else i for i in feature_vector]
        feature_vector = ','.join(feature_vector)
        print("\n\n\nFeature vector: ", feature_vector, "\n\n\n", flush=True)

        return feature_vector

    if solver_type == "sat":
        feature_vector_dict = gf.generate_features(inst)
        feature_vector = ",".join(str(x) for x in feature_vector_dict.values())
        return feature_vector
        
       

def get_nearest_neighbors(feat_vect, k, solver_type):
    print("\n\n", flush=True)
    print("feat_vect: ", feat_vect, flush=True)

    #feat_vect = [float(i) for i in feat_vect.split(',')]

    print("feat_vect: ", feat_vect, flush=True)
    print("type feat_vect: ", type(feat_vect), flush=True)

    kb_features = kb.get_all_feature_vectors(solver_type)
    if kb_features == None:
        return feat_vect
    
    kb_features = ast.literal_eval(kb_features)
    print("before removal: ", kb_features, flush=True)
    #kb_features.remove(feat_vect)

    print("kb_features: ", kb_features, flush=True)
    
    print("len(kb_features): ", len(kb_features), flush=True)
    print("k: ", k, flush=True)
    if len(kb_features) >= k:
        distances = [euclidean_distance(feat_vect, kb_feature) for kb_feature in kb_features]
    else:  
        return kb_features

    print("distance: ", distances, flush=True)

    nearest_indices = np.argsort(distances)[:k]
    print("nearest_indices: ", nearest_indices, flush=True)

    nearest_neighbors = [kb_features[i] for i in nearest_indices]
    print("nearest_neighbors: ", nearest_neighbors, flush=True)
    print("\n\n", flush=True)
    return nearest_neighbors


def get_sub_portfolio(similar_insts, solvers, T, solver_type):


    # Generate all possible subsets of solvers
    subsets = []
    for r in range(1, len(solvers)):
        subsets.extend(combinations(solvers, r))
    
    data_str = kb.matrix(solvers, similar_insts, T, solver_type)
    data = ast.literal_eval(data_str)

    distinct_numbers = set()
    for item in data:
        for subitem in item:
            if isinstance(subitem, int):
                distinct_numbers.add(subitem)
    distinct_numbers = len(distinct_numbers)
    print(f"There are {distinct_numbers} distinct numbers in the data.")
    # Create a dictionary where each key is a solver and the value is a list of the times it took to solve the problems
    solver_to_times = {}
    for solver, problem, time in data:
        if time != "T":
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(int(time))
    print(solver_to_times)
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
    T = 1800
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
        average_time = total_subset_time / (distinct_numbers*len(subset))
        if total_time <= T and count >= max_solved_instances:
            if count > max_solved_instances or (count == max_solved_instances and total_time < min_time):
                best_subsets.clear()
                best_subsets[subset] = (count, average_time)
                max_solved_instances = count
                min_time = total_time
            elif count == max_solved_instances and total_time == min_time:
                best_subsets[subset] = (count, average_time)
    
    return list(next(iter(best_subsets)))


def get_max_solved(solvers, similar_insts, T, solver_type):
    print("solvers FROM sunny get max solved: ", solvers, flush=True)
    

    if not (isinstance(solvers, list)):
        solvers = [solvers]
    
    max_solved = 0
    for solver in solvers:
        solver_solves_instances = kb.get_solved_times(solver, similar_insts, solver_type)
        solver_solves_instances = ast.literal_eval(solver_solves_instances)
        solver_solves_instances = [float(x) for x in solver_solves_instances]

        time_spent = 0
        i = 0
        print("T: ", T, flush=True)
        while time_spent < T and i < len(solver_solves_instances):

            max_solved += 1
            time_spent += float(solver_solves_instances[i])
            i += 1
    print("the max solved is: ", max_solved, flush=True)
    return max_solved

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

