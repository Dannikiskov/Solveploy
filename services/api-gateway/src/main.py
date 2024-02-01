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

class Solvers(Resource):
    def get(self):
        data = {"instructions": "get_solvers", "queue_name": "solverhandler", "identifier": str(uuid.uuid4())}
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

class StartSolvers(Resource):
    def post(self):
        data = request.json
        data["identifier"] = data["item"]["solver_identifier"]
        data["instructions"] = "start_solver"
        data["queue_name"] = "solverhandler"
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

api.add_resource(Solvers, '/api/solvers')
api.add_resource(StartSolvers, '/api/startsolver')



def async_execute(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: mq.send_wait_receive(data))
        response = future.result()
        return response
    


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
