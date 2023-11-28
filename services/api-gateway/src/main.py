from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import messageQueue

app = Flask(__name__)
api = Api(app)
CORS(app)
mq = messageQueue.MessageQueue()
class SolverJob(Resource):
    def get(self):
        job_id = mq.sendJob("testdata")
        result = mq.waitForResult(job_id)
        return {'result': result}

    def post(self):
        data = request.get_json()
        return {'message': 'Data received', 'data': data}

    def put(self):
        data = request.get_json()
        return {'message': 'Data updated', 'data': data}

api.add_resource(SolverJob, '/api/solverjob')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
