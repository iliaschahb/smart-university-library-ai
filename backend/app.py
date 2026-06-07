from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Bienvenue dans Smart University Library AI",
        "status": "API Flask opérationnelle",
        "version": "1.0.0"
    })


@app.route("/health")
def health_check():
    return jsonify({
        "status": "OK",
        "service": "backend-flask"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)