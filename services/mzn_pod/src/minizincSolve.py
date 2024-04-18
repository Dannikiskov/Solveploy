import minizinc
import tempfile
import os
import time

def run_minizinc_model(model_string, solver_name, data_string=None,):
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
                temp_data_file.write(data_string)
                instance.add_file(temp_data_file.name)
        
    except Exception as e:
        print("Error creating instance:", str(e))

    
    print("START SOLVER", flush=True)
    # Solve the MiniZinc model
    
    start_time = time.time()

    try:
        result = instance.solve()
    except Exception as e:
        print("Error solving the MiniZinc model:", str(e))
        return {"result": f"Error solving the MiniZinc model:, {str(e)}", "executionTime": "N/A"}

    end_time = time.time()

    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")


    # Print the result
    print("CLOSING TEMP FILE", flush=True)
    temp_model_file.close()
    if data_string is not None:
        temp_data_file.close()

    # Clean up temporary files
    print("REMOVING TEMP FILE", flush=True)
    os.remove(temp_model_path)
    if data_string is not None:
        os.remove(temp_data_file.name)

    print("RESULT: \n ", result, flush=True)

    result_dict = {"result": str(result.solution), "executionTime": execution_time}
    if result:
        return result_dict
    else:
        return {"result": "No result found.", "executionTime": execution_time}










def run_minizinc_model(model_string, data_string=None, solver_name='gecode'):
    # Write the MiniZinc model string to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mzn', delete=False) as temp_model_file:
        temp_model_file.write(model_string)
        temp_model_path = temp_model_file.name

    # Create a MiniZinc model
    model = minizinc.Model(temp_model_path)

    # Get a solver instance by name
    solver = minizinc.Solver.lookup(solver_name)

    try:
        # Create an instance of the MiniZinc model with the solver
        instance = minizinc.Instance(solver, model)

        # If a data string is provided, write it to a temporary file and add the file to the instance
        if data_string is not None:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.dzn', delete=False) as temp_data_file:
                temp_data_file.write(data_string)
                instance.add_file(temp_data_file.name)

        # Solve the MiniZinc model
        result = instance.solve()
    except Exception as e:
        print("Error:", str(e))

    
    return result