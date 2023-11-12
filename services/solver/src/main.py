from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
import minizinc
import tempfile

app = Flask(__name__)
app.config["JSONIFY_MIMETYPE"] = "application/json"
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api", methods=["GET"])
@cross_origin()
def get_api_data():
    return jsonify({"message": "This is the API data. Hello"})

@app.route("/api/solver", methods=["POST"])
@cross_origin()
def solver():
    model_string = request.get_json()["model_string"]
    # Run the MiniZinc model and get the results.
    solver_results = run_minizinc_model(model_string)
    print("RESPONSE: ", solver_results)
    # Set the Content-Type header to application/json.
    response = jsonify(solver_results)

    # Return the results in JSON format.
    return response


def run_minizinc_model(model_string, solver_name="gecode"):
    """Runs a MiniZinc model and returns the output.

    Args:
        model_string: The MiniZinc model string.
        solver_name: The name of the MiniZinc solver to use.

    Returns:
        A list containing dictionaries for each solution of the MiniZinc model.
    """

    # Create a temporary file and write the model string to it
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".mzn") as temp_file:
        temp_file.write(model_string)
        temp_file_path = temp_file.name

    try:
        # Run the MiniZinc model and get the results.
        model = minizinc.Model(temp_file_path)
        solver = minizinc.Solver.lookup(solver_name)
        instance = minizinc.Instance(solver, model)
        result = instance.solve()
        print(str(result))
        return str(result)

    finally:
        # Clean up: Remove the temporary file
        os.remove(temp_file_path)
  



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)



