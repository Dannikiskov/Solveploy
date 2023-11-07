from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["*"], allow_methods=["*"])

@app.route("/api", methods=["GET"])
@cross_origin()
def get_api_data():
    return jsonify({"message": "This is the API data. Hello"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
