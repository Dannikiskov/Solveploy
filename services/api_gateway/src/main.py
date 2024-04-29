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
        if data["mznFileContent"] is None or data["mznFileContent"] == "":
            return {"result": "Mzn file content is required"}
        
        data["identifier"] = data["item"]["jobIdentifier"]
        data["queueName"] = "jobHandler"
        result = async_execute(data)
        result_json = json.loads(result)
        print("RESULT POST JOB: ", result_json, flush=True)
        return result_json
    

    def delete(self):
        try:
            data = request.json
        except Exception as e:
            return {"result": "Invalid request body"}
        data["identifier"] = data["item"]["jobIdentifier"]
        data["instructions"] = "StopJob"
        data["queueName"] = "jobHandler"
        result = async_execute(data)

        return result

class Sunny(Resource):

    def post(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "Sunny"
        data["queueName"] = "jobHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json


class SolversMzn(Resource):

    def get(self):
        print("GETTING SOLVERS", flush=True)
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


class SolversMaxsat(Resource):

    def get(self):
        data = {"instructions": "GetAvailableMaxsatSolvers", "queueName": "jobHandler", "identifier": str(uuid.uuid4())}
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

    def post(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "AddMaxsatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def put(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "UpdateMaxsatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    
    def delete(self):
        data = request.json
        data["identifier"] = str(uuid.uuid4())
        data["instructions"] = "DeleteMaxSatSolver" 
        data["queueName"] = "kbHandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json

class K8s(Resource):
    def get(self):
        data = {"instructions": "GetAvailableK8sResources", "queueName": "kbHandler", "identifier": str(uuid.uuid4())}
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json


class results(Resource):
    
    def get(self, type):
        result = None
        if type == "mzn":
            result = mq.consume_one("mzn-result-queue")
        elif type == "sat":
            result = mq.consume_one("sat-result-queue")
        elif type == "maxsat":
            result = mq.consume_one("maxsat-result-queue")
        
        print("RESULT: ", result, flush=True)
        if result is None:
            return None
        return json.loads(result)

api.add_resource(Jobs, '/api/jobs')
api.add_resource(Sunny, '/api/jobs/sunny')
api.add_resource(SolversMzn, '/api/solvers/mzn')
api.add_resource(SolversSat, '/api/solvers/sat')
api.add_resource(SolversMaxsat, '/api/solvers/maxsat')
api.add_resource(K8s, '/api/k8s/resource')
api.add_resource(results, '/api/results/<string:type>')


def async_execute(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: mq.send_wait_receive(data))
        response = future.result()
        return response
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
