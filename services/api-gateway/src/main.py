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

mzn_string = """
int: nc = 3;

var 1..nc: wa;   var 1..nc: nt;  var 1..nc: sa;   var 1..nc: q;
var 1..nc: nsw;  var 1..nc: v;   var 1..nc: t;

constraint wa != nt;
constraint wa != sa;
constraint nt != sa;
constraint nt != q;
constraint sa != q;
constraint sa != nsw;
constraint sa != v;
constraint q != nsw;
constraint nsw != v;
solve satisfy;

output ["wa=\(wa)\t nt=\(nt)\t sa=\(sa)\n",
        "q=\(q)\t nsw=\(nsw)\t v=\(v)\n",
         "t=", show(t),  "\n"];
"""

class SolverHandler(Resource):
    
    def get(self):
        data = {}
        data["instructions"] = "GetSolvers"
        data["identifier"] = str(uuid.uuid4())
        data["queue_name"] = "knowledge-base"
        result = async_execute(data)
        result_json = json.loads(result)
        print(type(result_json), flush=True)
        print("---------------", flush=True)
        print(result_json, flush=True)
        result_dict = {item[0]: item[1] for item in result_json}
        return result_dict
    

class StartSolvers(Resource):
    def post(self):
        data = request.json
        data = {'content': data}
        data["instructions"] = "StartSolvers"
        data["mzn"] = mzn_string
        data["identifier"] = str(uuid.uuid4())
        data["queue_name"] = "solverhandler"
        print("DATA: ", data, flush=True)
        result = async_execute(data)
        result_json = json.loads(result)

        return result_json
    

api.add_resource(SolverHandler, '/api/solverhandler')
api.add_resource(StartSolvers, '/api/startsolvers')




def async_execute(data):

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(lambda: messageQueue.send_wait_receive(data))
        response = future.result()
        return response
    


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
