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
        # Get the JSON data from the request
        data = request.json

        # Add an "instructions" field to the JSON data
        data["instructions"] = "StartSolver"
        data["identifier"] = str(uuid.uuid4())

        # Print the modified JSON data
        print(json.dumps(data, indent=2), flush=True)

        # Process the job asynchronously
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.process_job, data, data["identifier"])
            response = future.result()

        return response

    def process_job(self, data, identifier):
        # Process the job and publish it to the message queue
        request_queue = messageQueue.RequestQueue(identifier)
        request_queue.publish(data)
        result = request_queue.consume()
        # Return a response (this part may need adjustment based on your use case)
        return result

    
class SolverDatabase(Resource):
    def post(self):
        data = request.json
        # Add an "instructions" field to the JSON data
        data["instructions"] = "PostSolverDBData"
        data["identifier"] = str(uuid.uuid4())

        # Print the modified JSON data
        print("HAEHEHEAHFHAEH")
        print(json.dumps(data, indent=2), flush=True)

        # Process the job asynchronously
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.process_job, data, data["identifier"])
            response = future.result()

        return response

    def process_job(self, data, identifier):
        # Process the job and publish it to the message queue
        request_queue = messageQueue.RequestQueue(identifier)
        request_queue.publish(data)
        result = request_queue.consume()
        # Return a response (this part may need adjustment based on your use case)
        return result

api.add_resource(SolverJob, '/api/solverjob')
api.add_resource(SolverDatabase, '/api/solver-database')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
