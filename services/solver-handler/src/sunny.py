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
    portfolio = []
    total_time = 0

    sorted_solvers = sorted(solvers, key=lambda x: (get_max_solved(x, similar_insts), -kb.get_average_solving_time(similar_insts[0], x)), reverse=True)

    for solver in sorted_solvers:
        solver_slots = get_max_solved(solver, similar_insts, T)
        solver_time = solver_slots * (T / len(sorted_solvers))

        if total_time + solver_time <= T:
            portfolio.append((solver, solver_time))
            total_time += solver_time
        else:
            break

    return portfolio


def get_max_solved(solver, similar_insts, T):
    max_solved = 0
    avg_time = float('inf')  # Initialize with infinity for tie-breaking
    for inst in similar_insts:
        solved = kb.get_solved_count(inst, solver, T)
        avg_inst_time = kb.get_average_solving_time(inst, solver)

        if solved > max_solved or (solved == max_solved and avg_inst_time < avg_time):
            max_solved = solved
            avg_time = avg_inst_time

    return max_solved


def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))


def get_stored_feature_vectors():
    # Placeholder implementation
    pass