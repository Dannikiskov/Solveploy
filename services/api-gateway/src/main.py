from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue
import concurrent.futures
import json
import uuid

app = Flask(__name__)
api = Api(app)
CORS(app)

class SolverJob(Resource):
    def post(self):
        data = request.json
        data["instructions"] = "StartSolver"
        data["identifier"] = str(uuid.uuid4())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.process_job, data, data["identifier"])
            response = future.result()

        return response

    def process_job(self, data, identifier):
        request_queue = messageQueue.RequestQueue(identifier)
        request_queue.publish(data)
        result = request_queue.consume()
        return result

    
class SolverDatabase(Resource):
    def post(self):
        data = request.json
        data["instructions"] = "PostSolverDBData"
        data["identifier"] = str(uuid.uuid4())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.process_job, data, data["identifier"])
            response = future.result()

        return response

    def process_job(self, data, identifier):
        request_queue = messageQueue.RequestQueue(identifier)
        request_queue.publish(data)
        result = request_queue.consume()
        return result

api.add_resource(SolverJob, '/api/solverjob')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
