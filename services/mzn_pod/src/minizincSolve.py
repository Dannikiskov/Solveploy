import time
import minizinc
import tempfile
import os

def run_minizinc_model(model_string, solver_name, data_string=None, data_type=None, params_dict=None, objective_list=None):
    if solver_name == "or tools cp-sat":
        solver_name = "sat"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mzn', delete=False) as temp_model_file:
        temp_model_file.write(model_string)
        temp_model_path = temp_model_file.name
        temp_model_file.close()

    model = minizinc.Model(temp_model_path)

    solver = minizinc.Solver.lookup(solver_name)

    instance = minizinc.Instance(solver, model)

    if data_string is not None:
        with tempfile.NamedTemporaryFile(mode='w', suffix=data_type, delete=False) as temp_data_file:
            temp_data_file.write(data_string)
            temp_data_file.close()
            instance.add_file(temp_data_file.name)

    try:
        if params_dict is not None:
            t1 = time.time()
            result = instance.solve(**params_dict)
            t2 = time.time() - t1
        else:
            t1 = time.time()
            result = instance.solve()
            t2 = time.time() - t1
    except Exception as e:
        print("Error while solving: ", e, flush=True)

        
    os.remove(temp_model_path)

    if data_string is not None:
        os.remove(temp_data_file.name)

    if result is not None:
        output = str(result.solution)
        if result.objective is not None:
            opt_val = result.objective
        else:
            opt_val = "N/A"
    else:
        output = "N/A"

    if params_dict is None:
        execution_time = t2 * 1000
    elif params_dict is not None and "--time-limit" in params_dict:
        if t2 * 1000 >= params_dict["--time-limit"]:
            execution_time = params_dict["--time-limit"]
        else: 
            execution_time = t2 * 1000
    else:
        execution_time = "N/A"

    return {"result": output, "executionTime": execution_time, "status": str(result.status), "optVal": opt_val, "optGoal": objective_list}