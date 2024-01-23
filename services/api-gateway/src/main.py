from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue
import concurrent.futures
import uuid

app = Flask(__name__)
api = Api(app)
CORS(app)

class SolverHandler(Resource):
    def post(self):
        data = request.json
        data["instructions"] = "StartSolver"
        data["identifier"] = str(uuid.uuid4())
        data["queue_name"] = "solverhandler"
        result = async_execute(data)
        return result
    

api.add_resource(SolverHandler, '/api/solverhandler')



def async_execute(data):

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: messageQueue.send_wait_receive(data))
        response = future.result()
        return response
    


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
