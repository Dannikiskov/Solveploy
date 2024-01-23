import minizinc
import tempfile
import os

def run_minizinc_model(model_string, data_path=None, solver_name='gecode'):
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

    print("CREATING INSTANCE", flush=True)
    # Create an instance of the MiniZinc model with the solver
    instance = minizinc.Instance(solver, model)

    print("START SOLVER", flush=True)
    # Solve the MiniZinc model
    try:
        result = instance.solve()
    except Exception as e:
        print("An error occurred:", str(e), flush=True)
        return "Error occurred during solving."

    # Print the result
    print("CLOSING TEMP FILE", flush=True)
    temp_model_file.close()
    print("REMOVING TEMP FILE", flush=True)
    print("RESULT: \n ", result, flush=True)
    if result:
        return str(result)
    else:
        return "No solution found."
