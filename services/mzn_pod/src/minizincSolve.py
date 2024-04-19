import json
import multiprocessing
import minizinc
import tempfile
import os
import time
import pymzn

def run_minizinc_model(model_string, solver_name, data_string=None, data_type=None):
    # Write the MiniZinc model string to a temporary file
    print("ATTEMPTING CREATE TEMP FILE:", flush=True)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mzn', delete=False) as temp_model_file:
        temp_model_file.write(model_string)
        temp_model_path = temp_model_file.name

    print("TEMP CREATED: ", temp_model_file.name, flush=True)

    # Create a MiniZinc model
    print("CREATING MODEL", flush=True)
    model = minizinc.Model(temp_model_path)

    print("CREATING SOLVER", flush=True)
    # Get a solver instance by name

    solver = minizinc.Solver.lookup(solver_name)


    try:
                
        print("CREATING INSTANCE", flush=True)
        # Create an instance of the MiniZinc model with the solver
        instance = minizinc.Instance(solver, model)

        if data_string is not None:

            with tempfile.NamedTemporaryFile(mode='w', suffix='.dzn', delete=False) as temp_data_file:
                if data_type == "json":
                    data_dict = json.loads(data_string)
                    data_string_list = pymzn.dict2dzn(data_dict)
                    for data_line in data_string_list:
                        temp_data_file.write(data_line)
                else:
                    temp_data_file.write(data_string)
                temp_data_file.close()
                with open(temp_data_file.name, 'r') as f:
                    print("DATA FILE CONTENTS: \n", f.read(), flush=True)
                instance.add_file(temp_data_file.name)
            
    except Exception as e:
        print("Error creating instance:", str(e))

    
    return_dict = {}

    print("START SOLVER", flush=True)
    # Solve the MiniZinc model
    
    try:

        def solve_instance(instance, return_dict):
            start_time = time.time()
            result = instance.solve()
            end_time = time.time()
            return_dict['result'] = str(result)
            print("RESULT: ", result, flush=True)
            return_dict['executionTime'] = end_time - start_time
            
        manager = multiprocessing.Manager()
        return_dict = manager.dict()

        p = multiprocessing.Process(target=solve_instance, args=(instance, return_dict))
        p.start()
        p.join()
        
    except Exception as e:
        print("Error solving the MiniZinc model:", str(e))
        return {"result": f"Error solving the MiniZinc model: {str(e)}", "executionTime": "N/A"}



    print("Execution time:", return_dict["executionTime"], " seconds")


    # Print the result
    print("CLOSING TEMP FILES", flush=True)
    temp_model_file.close()
    if data_string is not None:
        temp_data_file.close()

    # Clean up temporary files
    print("REMOVING TEMP FILES", flush=True)
    os.remove(temp_model_path)
    if data_string is not None:
        os.remove(temp_data_file.name)

    print("RESULT: \n ", return_dict, flush=True)
    return_dict = dict(return_dict)
    return return_dict

