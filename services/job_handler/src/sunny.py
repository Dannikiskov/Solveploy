from itertools import combinations
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
    sub_portfolio = get_sub_portfolio(similar_insts, solvers, solver_type)
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


def get_sub_portfolio(similar_insts, solvers, solver_type):


    # Generate all possible subsets of solvers
    subsets = []
    for r in range(1, len(solvers)):
        subsets.extend(combinations(solvers, r))
    
    # print("subset", subsets, flush=True)
    max_solved = 0
    best_subsets = {}
    solver_solve_times = {}
    for subset in subsets:
        print("subset: ", subset, flush=True)
        solved_instances_num = 0
        solved_instances_list = []
        for instance in similar_insts:
            # print("instance: ", instance, flush=True) 
            for solver in subset:
                # print("solver: ", solver, flush=True)
                if instance not in solved_instances_list and kb.is_instance_solved(instance, solver, solver_type):
                    if solver not in solver_solve_times or instance not in solver_solve_times[solver]:
                        solver_solve_times.setdefault(solver, []).append(kb.get_solved_time(solver, instance, solver_type))
                    solved_instances_list.append(instance)
                    solved_instances_num += 1
        print("subset: ", subset,  "solves ", solved_instances_num, " instances", flush=True)
        
        # Update the maximum number of solved instances and the selected solvers
        print("max_solved: ", max_solved, flush=True)
        print("solved_instances_num: ", solved_instances_num, flush=True)
        if solved_instances_num >= max_solved:
            if solved_instances_num > max_solved:
                best_subsets.clear()
                best_subsets[subset] = solved_instances_num
                max_solved = solved_instances_num
            else:
                best_subsets[subset] = solved_instances_num
            print("best_subsets: ", best_subsets, flush=True)

    print("SOLVE TIMER", flush=True)            
    print(solver_solve_times, flush=True)

    return best_subsets.keys()[0]


def get_max_solved(solvers, similar_insts, T, solver_type):
    print("solvers FROM sunny get max solved: ", solvers, flush=True)
    

    if not (isinstance(solvers, list)):
        solvers = [solvers]

    max_solved = 0
    for solver in solvers:
        solver_solves_instances = kb.get_solver_times(solver, similar_insts, solver_type)
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

