from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route("/api/", methods=["GET"])
@cross_origin()
def get_api_data():
    return jsonify({"message": "This is the API data. Hello"})

if __name__ == "__main__":
    app.run(debug=True)