import datetime
import json
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue as mq
import concurrent.futures
from kubernetes import client, config
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024 # 1000MB
api = Api(app)
CORS(app)
class Jobs(Resource):
    def post(self):
        data = request.json
        
        data["identifier"] = data["item"]["jobIdentifier"]
        data["queueName"] = "jobHandler"
        if "noresult" in data and data["noresult"] == True:
            async_execute_no_response(data)
        else:
            result = async_execute(data)
            try:
                result_json = json.loads(result)
            except Exception as e:
                return "JSON ERROR"
            return result_json
    

    def delete(self, solver_type=None, identifier=None):
        data = None
        if solver_type == "mzn":
            if identifier is not None:
                data = {"identifier": identifier, "instructions": "StopMznJob", "queueName": "jobHandler"}  
            else:
                data = {"instructions": "StopMznJobs", "queueName": "jobHandler"}
        elif solver_type == "sat":
            if identifier is not None:
                data = {"identifier": identifier, "instructions": "StopSatJob", "queueName": "jobHandler"}
            else:
                data = {"instructions": "StopSatJobs", "queueName": "jobHandler"}
        elif solver_type == "maxsat":
            if identifier is not None:
                data = {"identifier": identifier, "instructions": "StopMaxsatJob", "queueName": "jobHandler"}
            else:
                data = {"instructions": "StopMaxsatJobs", "queueName": "jobHandler"}
        
        async_execute_no_response(data)
        return "Job stop message sent"

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


class Results(Resource):
    
    def post(self):
        data = request.json
        result = mq.consume_one(f"{data['type']}-result-queue")
        
        
        if result is None:
            return None
        
        resultsList = []
        while result is not None:
            resultsList.append(json.loads(result))
            result = mq.consume_one(f"{data['type']}-result-queue")

        try:
            if data["optGoal"] == "minimize":
                lowest = resultsList[0]
                for res in resultsList:
                    if lowest["status"] == "SATISFIED" and res["status"] == "OPTIMAL_SOLUTION":
                        lowest = res
                    elif res["optVal"] < lowest["optVal"]:
                        lowest = res
                    elif res["optVal"] == lowest["optVal"] and res["executionTime"] < lowest["executionTime"]:
                        lowest = res
                if data["item"] != None:
                    if data["item"]["status"] == "SATISFIED" and lowest["status"] == "OPTIMAL_SOLUTION":
                        return lowest
                    elif lowest["optVal"] < data["item"]["optVal"]:
                        return lowest
                    elif lowest["optVal"] == data["item"]["optVal"] and lowest["executionTime"] < data["item"]["executionTime"]:
                        return lowest
                    else:
                        return None
                else:
                    return lowest
                
            if data["optGoal"] == "maximize":
                highest = resultsList[0]
                for res in resultsList:
                    if highest["status"] == "SATISFIED" and res["status"] == "OPTIMAL_SOLUTION":
                        highest = res
                    elif res["optVal"] > highest["optVal"]:
                        highest = res
                    elif res["optVal"] == highest["optVal"] and res["executionTime"] < highest["executionTime"]:
                        highest = res
                if data["item"] != None:
                    if data["item"]["status"] == "SATISFIED" and highest["status"] == "OPTIMAL_SOLUTION":
                        return highest
                    elif highest["optVal"] > data["item"]["optVal"]:
                        return highest
                    elif highest["optVal"] == data["item"]["optVal"] and highest["executionTime"] < data["item"]["executionTime"]:
                        return highest
                    else:
                        return None
                else:
                    return highest
                
            elif data["optGoal"] == "satisfy":
                fastest = resultsList[0]
                for res in resultsList:
                    if res["status"] == "SATISFIED" and fastest["status"] == "SATISFIED":
                        if res["executionTime"] < fastest["executionTime"]:
                            fastest = res
                if data["item"] != None and data["item"]["executionTime"] < fastest["executionTime"]:
                    return None
                return fastest
                
        except Exception as e:
            return None
        
        return None

class Webhook(Resource):

    def post(self, deployment_name=None):
        data = request.json
        # Extract repository and tag information if needed
        repo_name = data['repository']['name']
        tag = data['push_data']['tag']
        # Define the deployment name and namespace
        deployment_name = deployment_name
        namespace = "default"
        # Patch the deployment to trigger a rolling restart
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": f"{datetime.datetime.now().isoformat()}"
                        }
                    }
                }
            }
        }
        config.load_incluster_config()

        api_instance = client.AppsV1Api()
        
        api_instance.patch_namespaced_deployment(deployment_name, namespace, body)
        
        return jsonify({'status': 'success'})


class Data(Resource):
        def get(self, data_type=None):
            if data_type=="mzn":
                data = {"instructions": "GetMznData", "queueName": "kbHandler", "identifier": str(uuid.uuid4())}
                result = async_execute(data)
                result_json = json.loads(result)
                return result_json
        
            elif data_type=="sat":
                data = {"instructions": "GetSatData", "queueName": "kbHandler", "identifier": str(uuid.uuid4())}
                result = async_execute(data)
                result_json = json.loads(result)
                return result_json
            
            elif data_type=="maxsat":
                data = {"instructions": "GetMaxsatData", "queueName": "kbHandler", "identifier": str(uuid.uuid4())}
                result = async_execute(data)
                result_json = json.loads(result)
                return result_json
    

api.add_resource(Jobs, '/api/jobs', '/api/jobs/<string:solver_type>', '/api/jobs/<string:solver_type>/<string:identifier>')
api.add_resource(Sunny, '/api/sunny')
api.add_resource(SolversMzn, '/api/solvers/mzn')
api.add_resource(SolversSat, '/api/solvers/sat')
api.add_resource(SolversMaxsat, '/api/solvers/maxsat')
api.add_resource(K8s, '/api/k8s/resource')
api.add_resource(Results, '/api/results')
api.add_resource(Webhook, '/api/imageupdate/<string:deployment_name>')
api.add_resource(Data, '/api/data/<string:data_type>')


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
