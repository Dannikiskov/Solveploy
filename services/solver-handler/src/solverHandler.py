import pika
import os
import solverK8Job
import threading
import json
import time
import messageQueue
import minizinc
import sys
import re
import subprocess
import numpy as np

def sunny(inst, solvers, bkup_solver, k, T, KB):
    # Get features vector for the given instance
    feat_vect = get_features(inst)

    # Find k-nearest neighbors
    similar_insts = get_nearest_neighbors(feat_vect, k, KB)

    # Get sub-portfolio
    sub_portfolio = get_sub_portfolio(similar_insts, solvers, KB)

    # Initialize variables
    slots = sum(get_max_solved(s, similar_insts, KB, T) for s in sub_portfolio)
    time_slot = T / slots
    tot_time = 0
    schedule = {bkup_solver: 0}

    # Populate the schedule
    for solver in sub_portfolio:
        solver_slots = get_max_solved(solver, similar_insts, KB, T)
        schedule[solver] = solver_slots * time_slot
        tot_time += solver_slots * time_slot

    # Adjust backup solver time
    if tot_time < T:
        schedule[bkup_solver] += T - tot_time

    # Return sorted schedule
    return sorted(schedule.items(), key=lambda x: x[1]), similar_insts, KB

# Define placeholder functions (replace with actual implementations)
def get_features(inst):
    command = ["mzn2feat", "-i", inst]
    result = subprocess.run(command, capture_output=True, text=True)
    features = result.stdout.strip()
    features_list = [float(number) for number in features.split(",")]

    return features_list

def get_nearest_neighbors(feat_vect, k, KB):
    kb_features = get_stored_feature_vectors()
    # Calculate distances to all feature vectors
    distances = [euclidean_distance(feat_vect, kb_feature) for kb_feature in kb_features]

    # Get indices of k smallest distances
    nearest_indices = np.argsort(distances)[:k]

    # Return the k nearest neighbors and their distances
    nearest_neighbors = [(kb_features[i], distances[i]) for i in nearest_indices]
    return nearest_neighbors

def get_sub_portfolio(similar_insts, solvers, KB):
    portfolio = []
    total_time = 0
    # Sort solvers based on getMaxSolved in descending order
    sorted_solvers = sorted(solvers, key=get_max_solved, reverse=True)

    # Get the initial sub-portfolio
    current_sub_portfolio = get_sub_portfolio(sorted_solvers, similar_insts, KB)

    for solver in current_sub_portfolio:
        solver_slots = get_max_solved(solver)
        solver_time = solver_slots * (T / len(current_sub_portfolio))

        if total_time + solver_time <= T:
            portfolio.append((solver, solver_time))
            total_time += solver_time
        else:
            break

    return portfolio

def get_max_solved(solver, similar_insts, KB, T):
    # Placeholder implementation
    pass


def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

def get_stored_feature_vectors():
    # Placeholder implementation
    pass
    


if __name__ == "__main__":
    output = get_features(sys.argv[1])
    print(output)

