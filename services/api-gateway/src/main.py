from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue
import base64
import uuid 
app = Flask(__name__)
api = Api(app)
CORS(app)

class SolverJob(Resource):
    def post(self):
        job_queue = messageQueue.SolverJobQueue()
        model_meta_data = request.json['message']
        #model_meta_data['job_id'] = "job-"+str(uuid.uuid4())[:8]
        print(model_meta_data, flush=True)
        job_queue.publish(model_meta_data)
        response = job_queue.consume()
        print("REPONSE API:", response, flush=True)
        return response

api.add_resource(SolverJob, '/api/solverjob')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
