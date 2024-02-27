from itertools import combinations
import subprocess
import numpy as np
import kb

def sunny(inst, solvers, bkup_solver, k, T):
    # Get features vector for the given instance
    feat_vect = get_features(inst)

    # Find k-nearest neighbors
    similar_insts = get_nearest_neighbors(feat_vect, k)

    # Get sub-portfolio
    sub_portfolio = get_sub_portfolio(similar_insts, solvers)

    # Initialize variables
    slots = sum(get_max_solved(s, similar_insts,  T) for s in sub_portfolio)
    time_slot = T / slots
    tot_time = 0
    schedule = {bkup_solver: 0}

    # Populate the schedule
    for solver in sub_portfolio:
        solver_slots = get_max_solved(solver, similar_insts, T)
        schedule[solver] = solver_slots * time_slot
        tot_time += solver_slots * time_slot

    # Adjust backup solver time
    if tot_time < T:
        schedule[bkup_solver] += T - tot_time

    # Return sorted schedule
    return sorted(schedule.items(), key=lambda x: x[1]), similar_insts


def get_features(inst):
    command = ["mzn2feat", "-i", inst]
    result = subprocess.run(command, capture_output=True, text=True)
    features = result.stdout.strip()
    features_list = [float(number) for number in features.split(",")]

    return features_list


def get_nearest_neighbors(feat_vect, k):
    kb_features = kb.get_all_feature_vectors()

    if kb_features is not None and len(kb_features) >= k:
        # Calculate distances to all feature vectors
        distances = [euclidean_distance(feat_vect, kb_feature) for kb_feature in kb_features]
    else:  
        return kb_features

    # Get indices of k smallest distances
    nearest_indices = np.argsort(distances)[:k]

    # Return the k nearest neighbors and their distances
    nearest_neighbors = [(kb_features[i], distances[i]) for i in nearest_indices]
    return nearest_neighbors


def get_sub_portfolio(similar_insts, solvers, T):
    max_solved = 0
    selected_solvers = []

    # Iterate through all possible subsets of solvers
    for subset_size in range(1, len(solvers) + 1):
        for subset in combinations(solvers, subset_size):
            instances_solved = set()
            total_solving_time = 0

            # Calculate total instances solved and total solving time for the subset
            for solver in subset:
                results = kb.get_solved_times(solver.id, similar_insts)

                for instance_id, solve_time in results:
                    instances_solved.add(instance_id)
                    total_solving_time += solve_time

            # Check if the current subset solves more instances and update if necessary
            if len(instances_solved) > max_solved or (len(instances_solved) == max_solved and total_solving_time / len(instances_solved) < selected_solvers[0][1]):
                max_solved = len(instances_solved)
                selected_solvers = [(solver, total_solving_time) for solver in subset]

    return [solver[0] for solver in selected_solvers]


def get_max_solved(solver, similar_insts, T):
    max_solved = 0

    solved_times = kb.get_solved_times(solver.id, similar_insts).sort(key=lambda x: x[3])
    
    for solve_time in solved_times:
        if solve_time < T:
            max_solved += 1
            T -= solve_time
    return max_solved


def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

