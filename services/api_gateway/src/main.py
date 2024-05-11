import json
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue as mq
import concurrent.futures
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 50 Megabytes
api = Api(app)
CORS(app)

class Jobs(Resource):

    def post(self):
        data = request.json
        if data["mznFileContent"] is None or data["mznFileContent"] == "":
            return {"result": "Mzn file content is required"}
        
        data["identifier"] = data["item"]["jobIdentifier"]
        data["queueName"] = "jobHandler"
        if "noresult" in data and data["noresult"] == True:
            async_execute_no_response(data)
        else:
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
    
    def post(self):
        data = request.json
        result = mq.consume_one(f"{data['type']}-result-queue")
        print("RESULT: ", result, flush=True)
        print("DATA: ", data, flush=True)
        resultsList = []
        
        while result is not None:
            resultsList.append(json.loads(result))
            print("RESULT LIST INSIDE: ", resultsList, flush=True)
            result = mq.consume_one(f"{data['type']}-result-queue")

        print("optgoal: ", data["optGoal"], flush=True)
        try:
            if data["optGoal"] == "minimize":
                lowest = resultsList[0]["optValue"]
                for res in resultsList:
                    if res["optValue"] < lowest:
                        lowest = res["optValue"]
                    if lowest < data["item"]["optValue"]:
                        print("Returning result: ", result, flush=True)
                        return lowest
                    else:
                        print("Returning None", flush=True)
                        return None
                    
            elif data["optGoal"] == "maximize":
                highest = resultsList[0]["optValue"]
                for res in resultsList:
                    if res["optValue"] > highest:
                        highest = res["optValue"]
                    if highest > data["item"]["optValue"]:
                        print("Returning result: ", result, flush=True)
                        return highest
                    else:
                        print("Returning None", flush=True)
                        return None
                    
            else:
                fastest = resultsList[0]
                for res in resultsList:
                    if res["status"] == "SATISFIED" and fastest["status"] == "SATISFIED":
                        if res["executionTime"] < fastest["executionTime"]:
                            fastest = res
                if data["item"] == None or fastest["executionTime"] < data["item"]["executionTime"]:
                    print("Returning result: ", fastest, flush=True)
                    return fastest
                
        except Exception as e:
            print("Error: ", e, flush=True)
            return None
            
            

        
        if result is None:
            return None
        
        return json.loads(result)

api.add_resource(Jobs, '/api/jobs')
api.add_resource(Sunny, '/api/jobs/sunny')
api.add_resource(SolversMzn, '/api/solvers/mzn')
api.add_resource(SolversSat, '/api/solvers/sat')
api.add_resource(SolversMaxsat, '/api/solvers/maxsat')
api.add_resource(K8s, '/api/k8s/resource')
api.add_resource(results, '/api/results')


def async_execute(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: mq.send_wait_receive(data))
        response = future.result()
        return response
    
def async_execute_no_response(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: mq.send(data))
        response = future.result()
        return response
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
