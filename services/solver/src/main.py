from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import jobs


#-----------------------------v CONFIG v-----------------------------#


app = Flask(__name__)
app.config["JSONIFY_MIMETYPE"] = "application/json"
CORS(app, resources={r"/api/*": {"origins": "*"}})


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)



