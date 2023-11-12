import os
import minizinc
import tempfile

def run_minizinc_model(model_string, solver_name="gecode"):
    """Runs a MiniZinc model and returns the output.

    Args:
        model_string: The MiniZinc model string.
        solver_name: The name of the MiniZinc solver to use.

    Returns:
        A dictionary containing the output of the MiniZinc model.
    """

    # Create a temporary file and write the model string to it
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".mzn") as temp_file:
        temp_file.write(model_string)
        temp_file_path = temp_file.name

    try:
        # Run the MiniZinc model and get the results.
        model = minizinc.Model(temp_file_path)
        solver = minizinc.Solver.lookup(solver_name)
        instance = minizinc.Instance(solver)
        result = instance.solve()


        return result.solution

    finally:
        # Clean up: Remove the temporary file
        os.remove(temp_file_path)