from itertools import combinations
import subprocess
import tempfile
import numpy as np
import kb
import messageQueue as mq
import ast



def sunny(inst, dataFile, dataType, solvers, bkup_solver, k, T, identifier, solver_type):
    # Get features vector for the given instance
    print("printing arguments", k, T, identifier, dataType, flush=True)
    print("\n\nGetting features vector for the given instance", flush=True)
    feat_vect = get_features(inst, dataFile, dataType)

    # Find k-nearest neighbors
    print("Finding k-nearest neighbors", flush=True)
    similar_insts = get_nearest_neighbors(feat_vect, k)

    # Get sub-portfolio
    print("Getting sub-portfolio", flush=True)
    sub_portfolio = get_sub_portfolio(similar_insts, solvers, solver_type)

    # Initialize variables
    print("Initializing variables", flush=True)
    slots = sum([get_max_solved(solver, similar_insts, T, solver_type) + (k - get_max_solved(sub_portfolio, similar_insts, T, solver_type)) for solver in sub_portfolio])
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
    print("Returning sorted schedule: ", sorted(schedule.items(), key=lambda x: x[1]), flush=True)
    mq.send_to_queue(sorted(schedule.items(), key=lambda x: x[1]), f"jobhandler-{identifier}")


def get_features(inst, data, data_type):
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
        print("\ndznIncluded\n", flush=True)
        command = ["mzn2feat", "-i", temp_file_mzn.name, "-d", temp_file_dzn.name]
    else:
        command = ["mzn2feat", "-i", temp_file_mzn.name]

    cmd_result = subprocess.run(command, capture_output=True, text=True)
    
    
    feature_vector = cmd_result.stdout.strip()
    feature_vector = feature_vector.split(',')
    feature_vector = [str(float(i)) if 'e' in i else i for i in feature_vector]
    feature_vector = ','.join(feature_vector)

    print("get_features feature_vector: ", feature_vector, flush=True)

    return feature_vector


def get_nearest_neighbors(feat_vect, k):
    print("\n\n", flush=True)
    print("feat_vect: ", feat_vect, flush=True)
    print("\n\n", flush=True)
    kb_features = kb.get_all_feature_vectors()

    kb_features =[kb_features]  # Now convert kb_features
    if kb_features is not None and len(kb_features) >= k:
        # Calculate distances to all feature vectors
        distances = [euclidean_distance(feat_vect, kb_features) for kb_feature in kb_features]
    else:  
        return kb_features

    # Get indices of k smallest distancesk
    nearest_indices = np.argsort(distances)[:k]

    # Return the k nearest neighbors and their distances
    nearest_neighbors = [(kb_features[i], distances[i]) for i in nearest_indices]
    return nearest_neighbors


def get_sub_portfolio(similar_insts, solvers, solver_type):
    max_solved = 0
    selected_solvers = []

    # Generate all possible subsets of solvers
    subsets = []
    for r in range(1, len(solvers) + 1):
        subsets.extend(combinations(solvers, r))
    

    # Iterate through each subset
    for subset in subsets:
        solved_instances = 0
        
        # Check how many instances can be solved using the current subset
        for instance in similar_insts:
            for solver in subset:
                if kb.is_instance_solved(instance, solver, solver_type):
                    solved_instances += 1
        
        # Update the maximum number of solved instances and the selected solvers
        if solved_instances > max_solved:
            max_solved = solved_instances
            selected_solvers = list(subset)
    

    return selected_solvers


def get_max_solved(solvers, similar_insts, T, solver_type):
    print("solvers FROM sunny get max solved: ", solvers, flush=True)

    if not (isinstance(solvers, list)):
        solvers = [solvers]

    max_solved = 0
    for solver in solvers:
        solver_solves_instances = kb.get_solver_times(solver["name"], similar_insts, solver_type)
        solver_solves_instances = ast.literal_eval(solver_solves_instances)
        print("solver_solves_instances", solver_solves_instances, flush=True)

        time_spent = 0
        i = 0
        while time_spent < T and i < len(solver_solves_instances):
            max_solved += 1
            time_spent += float(solver_solves_instances[i])
            i += 1

    return max_solved

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

