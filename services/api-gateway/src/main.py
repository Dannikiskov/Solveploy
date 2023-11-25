from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

class HelloWorld(Resource):
    def get(self):
        print("Endpoint GET: /api/hello    <--- HIT")
        return {'message': 'Hello, World!'}

    def post(self):
        data = request.get_json()  # Assumes the incoming data is in JSON format
        # Process the data as needed
        return {'message': 'Data received', 'data': data}

    def put(self):
        data = request.get_json()
        # Process the data as needed
        return {'message': 'Data updated', 'data': data}

api.add_resource(HelloWorld, '/api/hello')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
