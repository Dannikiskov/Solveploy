import io
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import jobs
import docker
import tempfile


#-----------------------------v CONFIG v-----------------------------#


app = Flask(__name__)
app.config["JSONIFY_MIMETYPE"] = "application/json"
CORS(app, resources={r"/api/*": {"origins": "*"}})


#-----------------------------v AUX FUNCTIONS v-----------------------------#

"""def build_image():

    dockerfile_content = b'
    # Use a base image that includes MiniZinc
    FROM minizinc/minizinc:latest

    # Create a directory for your MiniZinc application
    WORKDIR /app

    # Copy your MiniZinc model file into the container
    COPY . .

    # Define environment variables for the model string and solver name
    ENV MODEL_STRING=""
    ENV SOLVER_NAME="gecode"

    # Define the command to run your MiniZinc application, using MODEL_STRING
    CMD ["minizinc", "--solver", "$SOLVER_NAME", "$MODEL_STRING"]'

    # Convert the Dockerfile content to a file-like object
    dockerfile_obj = io.BytesIO(dockerfile_content)

    # Create a Docker client
    docker_client = docker.from_env()

    # Build the Docker image from the Dockerfile string
    image, build_logs = docker_client.images.build(
        fileobj=dockerfile_obj,
        rm=True,  # Remove intermediate containers
        tag='minizinc-job-image',
    )

    # Print build logs
    for log_entry in build_logs:
        print(log_entry)"""

#-----------------------------v ROUTES v-----------------------------# 


@app.route("/api", methods=["GET"])
@cross_origin()
def get_api_data():
    return jsonify({"message": "This is the API data. Hello"})


@app.route("/api/solver", methods=["POST"])
@cross_origin()
def solver():
    model_string = request.get_json()["model_string"]
    solver_results = jobs.start_minizinc_job(model_string)
    print("RESPONSE: ", solver_results)
    response = jsonify(solver_results)
    return response


#-----------------------------v INIT v-----------------------------# 


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)



