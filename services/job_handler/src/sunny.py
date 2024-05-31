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
    print("solvers", solvers, flush=True)

    # Get features vector for the given instance
    feat_vect = get_features(inst, solver_type, data_file, data_type)
    print("feat_vect", feat_vect, flush=True)

    # Find k-nearest neighbors
    similar_insts = get_nearest_neighbors(feat_vect, k, solver_type)
    print("len similar_insts", len(similar_insts), flush=True)

    # Get sub-portfolio
    sub_portfolio, matrix = get_sub_portfolio(similar_insts, solvers, T, solver_type)
    print("sub_portfolio", sub_portfolio, flush=True)
    print(";ATRIC\n", matrix, flush=True)

    # Initialize variables
    slots = sum([get_max_solved(solver, matrix, T) for solver in sub_portfolio]) + (k - get_max_solved(sub_portfolio, matrix, T))
    time_slot = T / slots
    tot_time = 0
    schedule = {bkup_solver['name']: 0}
    print("slots", slots, flush=True)
    print("time_slot", time_slot, flush=True)

    # Populate the schedule
    for solver in sub_portfolio:
        solver_slots = get_max_solved(solver, matrix, T)
        print("Solver: ", solver, "Slots: ", solver_slots, flush=True)
        schedule[solver] = solver_slots * time_slot
        tot_time += solver_slots * time_slot

    print("schedule", schedule, flush=True) 
    # Adjust backup solver time
    if tot_time < T:
        print("tot_time", tot_time, flush=True)
        print("T", T, flush=True)
        schedule[bkup_solver['name']] += T - tot_time

    schedule = {k: v for k, v in schedule.items() if v != 0}

    result = sort_by_average_solving_time(schedule, matrix, T)

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
    
    data_str = kb.matrix(solvers, similar_insts, T, solver_type)
    data = ast.literal_eval(data_str)
    print("DATA\n", data, flush=True)
    print(data, flush=True)
    distinct_numbers = len(set(item[1] for item in data))

    solver_to_times = {}
    problems = set()
    for solver, problem, time in data:
        problems.add(problem)
        if time != "T":
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(float(time))

    subsets = list(chain.from_iterable(combinations(solvers, r) for r in range(1, len(solvers))))

    solver_to_instances = {}
    for solver, instance, time in data:
        if time != "T":
            if solver not in solver_to_instances:
                solver_to_instances[solver] = {}
            solver_to_instances[solver][instance] = (float(time))

    max_solved_instances = 0
    best_subsets = {}
    
    for subset in subsets:
        print("subset", subset, flush=True)
        fastest_solved = {}
        total_time = 0
        solved_instances = set()
        total_subset_time = 0
        count = 0
        for solver in subset:
            print("solver", solver, flush=True)
            if solver in solver_to_instances:
                solved_instances.update(solver_to_instances[solver])
                total_subset_time += sum(solver_to_times[solver]) + T*(distinct_numbers-len(solver_to_instances[solver]))
                for problem in problems:
                    print("problem", problem, flush=True)
                    if problem in solver_to_instances[solver] and (problem not in fastest_solved or solver_to_instances[solver][problem] < fastest_solved[problem]):
                        fastest_solved[problem] = solver_to_instances[solver][problem]
                        print("fastest_solved", fastest_solved, flush=True)

        sorted_times = sorted(list(fastest_solved.values()))
        sorted_times = [time for time in sorted_times if time != "T"]
        for time in sorted_times:
            if total_time + time <= T:
                total_time += time
                count += 1

        average_time = total_subset_time / (distinct_numbers*len(subset))
        print("count", count,  "max_solved_instance", max_solved_instances, flush=True)
        if count > max_solved_instances:
            best_subsets.clear()
            best_subsets[subset] = (count, average_time)
            print("best_subsets", best_subsets, flush=True)
            max_solved_instances = count
        elif count == max_solved_instances:
            best_subsets[subset] = (count, average_time)
            print("best_subsets", best_subsets, flush=True)
    
    result = None
    lowest_avg = None  
    min_key_length = min(len(k) for k in best_subsets.keys())
    selected_entries = {k: v for k, v in best_subsets.items() if len(k) == min_key_length}
    best_subsets = selected_entries

    if len (best_subsets) > 1:
        print("len(best_subsets)", len(best_subsets), flush=True)
        for best_subset in best_subsets:
            print("best_subset", best_subset, flush=True)
            if result == None or best_subsets[best_subset][1] < lowest_avg:
                print("best_subsets[best_subset][1]", best_subsets[best_subset][1], flush=True)
                print("lowest_avg", lowest_avg, flush=True)
                result = best_subsets[best_subset]
                lowest_avg = best_subsets[best_subset][1]
    else: 
        result = best_subsets

    print("RESULT\n", result, flush=True)
    return (list(next(iter(result))), data)


def get_max_solved(solvers, data, T):
    if not (isinstance(solvers, list)):
        solvers = [solvers]
        
    distinct_numbers = len(set(item[1] for item in data))

    solver_to_times = {}
    problems = set()
    for solver, problem, time in data:
        problems.add(problem)
        if time != "T":
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(float(time))


    solver_to_instances = {}
    for solver, instance, time in data:
        if time != "T":
            if solver not in solver_to_instances:
                solver_to_instances[solver] = {}
            solver_to_instances[solver][instance] = (float(time))

    fastest_solved = {}
    total_time = 0
    solved_instances = set()
    total_subset_time = 0
    count = 0
    for solver in solvers:
        if solver in solver_to_instances:
            solved_instances.update(solver_to_instances[solver])
            total_subset_time += sum(solver_to_times[solver]) + T*(distinct_numbers-len(solver_to_instances[solver]))
            for problem in problems:
                if problem in solver_to_instances[solver] and (problem not in fastest_solved or solver_to_instances[solver][problem] < fastest_solved[problem]):
                    fastest_solved[problem] = solver_to_instances[solver][problem]

    sorted_times = sorted(list(fastest_solved.values()))
    for time in sorted_times:
        if total_time + time <= T:
            total_time += time
            count += 1
    
    return count

def sort_by_average_solving_time(schedule, matrix, T):
    solver_to_times = {}
    for solver, problem, time in matrix:
        if time != "T":
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(float(time))
        else:
            if solver not in solver_to_times:
                solver_to_times[solver] = []
            solver_to_times[solver].append(T)

    solver_to_instances = {}
    for solver, instance, time in matrix:
        if time != "T":
            if solver not in solver_to_instances:
                solver_to_instances[solver] = {}
            solver_to_instances[solver][instance] = float(time)
        else:
            if solver not in solver_to_instances:
                solver_to_instances[solver] = {}
            solver_to_instances[solver][instance] = T
    average_times = {}
    for solver in schedule:
        total_time = sum(solver_to_times[solver])
        total_time += (len(solver_to_instances[solver]) - len(solver_to_times[solver])) * schedule[solver]
        average_times[solver] = total_time / len(solver_to_instances[solver])
    print(average_times)
    sorted_solvers = sorted(average_times, key=average_times.get)
    sorted_schedule = {solver: schedule[solver] for solver in sorted_solvers}

    return sorted_schedule

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))

