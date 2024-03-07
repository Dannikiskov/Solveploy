import json
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue as mq
import concurrent.futures
import uuid

app = Flask(__name__)
api = Api(app)
CORS(app)

class Jobs(Resource):

    def post(self):
        data = request.json
        data["identifier"] = data["item"]["solverIdentifier"]
        data["queueName"] = "jobHandler"
        result = async_execute(data)
        result_json = json.loads(result)
        print("RESULT: ", result_json, flush=True)
        return result_json
    

    def delete(self):
        data = request.json
        data["identifier"] = data["item"]["solverIdentifier"]
        data["instructions"] = "StopJob"
        data["queueName"] = "jobHandler"
        result = async_execute(data)

        return result

class Sunny(Resource):

    def post(self):
        data = request.json
        data["identifier"] = data["item"]["solverIdentifier"]
        data["instructions"] = "Sunny"
        data["queueName"] = "jobHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json


class SolversMzn(Resource):

    def get(self):
        data = {"instructions": "GetAvailableMznSolvers", "queueName": "jobHandler", "identifier": str(uuid.uuid4())}
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

    def post(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "AddMznSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def put(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "UpdateMznSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def delete(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "DeleteMznSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
class SolversSat(Resource):

    def get(self):
        data = {"instructions": "GetAvailableSatSolvers", "queueName": "jobHandler", "identifier": str(uuid.uuid4())}
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

    def post(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "AddSatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def put(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "UpdateSatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def delete(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "DeleteSatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json



api.add_resource(Jobs, '/api/jobs')
api.add_resource(Sunny, '/api/jobs/sunny')
api.add_resource(SolversMzn, '/api/solvers/mzn')
api.add_resource(SolversSat, '/api/solvers/sat')


def async_execute(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: mq.send_wait_receive(data))
        response = future.result()
        return response
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
