import json
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app

from ml.predict_popularity import predict_by_book_id, predict_from_features


ml_bp = Blueprint("ml_bp", __name__)


def model_dir():
    return Path(current_app.root_path) / "ml" / "models"


@ml_bp.route("/ml/popularity/health", methods=["GET"])
def popularity_health():
    model_file = model_dir() / "popularity_model.joblib"
    metrics_file = model_dir() / "popularity_metrics.json"
    return jsonify({
        "model_exists": model_file.exists(),
        "metrics_exists": metrics_file.exists(),
        "model_file": str(model_file),
        "metrics_file": str(metrics_file),
    }), 200


@ml_bp.route("/ml/popularity/metrics", methods=["GET"])
def popularity_metrics():
    metrics_file = model_dir() / "popularity_metrics.json"
    if not metrics_file.exists():
        return jsonify({
            "error": "Fichier de métriques introuvable.",
            "hint": "Exécute : python backend/ml/train_popularity_model.py",
            "expected_path": str(metrics_file),
        }), 404

    with open(metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    return jsonify(metrics), 200


@ml_bp.route("/ml/popularity/predict/<int:book_id>", methods=["GET"])
def popularity_predict_by_book(book_id):
    try:
        result = predict_by_book_id(book_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@ml_bp.route("/ml/popularity/predict", methods=["POST"])
def popularity_predict_custom():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    try:
        result = predict_from_features(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
