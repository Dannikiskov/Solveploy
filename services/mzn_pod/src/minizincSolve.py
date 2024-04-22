import re
import minizinc
import tempfile
import os

def run_minizinc_model(model_string, solver_name, data_string=None, data_type=None, params_dict=None):

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


    result = instance.solve(**params_dict) if params_dict is not None else instance.solve()

    output = str(result.solution)

    os.remove(temp_model_path)

    if data_string is not None:
        os.remove(temp_data_file.name)

    match = re.search(r'solve maximize (\w+);', model_string)

    if match:
        objective = match.group(1)  # The first group is the string after "solve minimize"
        opt_val = result.solution.__dict__[objective]
    else:
        match = re.search(r'solve minimize (\w+);', model_string)
        if match:
            objective = match.group(1)  # The first group is the string after "solve minimize"
            opt_val = result.solution.__dict__[objective]
        else:
            opt_val = "N/A"

    if 'time' in result.statistics:
        execution_time = result.statistics['time'].total_seconds() * 1000
    else:
        execution_time = "N/A"

    return {"result": output, "executionTime": execution_time, "status": str(result.status), "optValue": opt_val}