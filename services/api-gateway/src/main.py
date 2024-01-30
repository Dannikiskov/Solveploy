import json
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue
import concurrent.futures
import uuid

app = Flask(__name__)
api = Api(app)
CORS(app)

class Solvers(Resource):
    
    def get(self):
        data = {}
        data["instructions"] = "GetSolvers"
        data["identifier"] = str(uuid.uuid4())
        data["queue_name"] = "solverhandler"
        result = async_execute(data)
        result_json = json.loads(result)
        print(type(result_json), flush=True)
        print("---------------", flush=True)
        print(result_json, flush=True)
        #result_dict = {item[0]: item[1] for item in result_json}
        return result_json
    

class StartSolvers(Resource):
    def post(self):
        data = request.json
        data["instructions"] = "StartSolver"
        data["identifier"] = str(uuid.uuid4())
        data["queue_name"] = "solverhandler"
        #print("DATA: ", data, flush=True)
        result = async_execute(data)
        result_json = json.loads(result)
        print(type(result_json), flush=True)
        print("RESULT: ", result_json, flush=True)

        return result_json
    

api.add_resource(Solvers, '/api/solvers')
api.add_resource(StartSolvers, '/api/startsolver')



def async_execute(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: messageQueue.send_wait_receive(data))
        response = future.result()
        return response
    


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
