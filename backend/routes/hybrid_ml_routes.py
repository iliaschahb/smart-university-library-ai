import json
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app

from ml.predict_hybrid_demand import predict_for_book, predict_from_row

hybrid_ml_bp = Blueprint("hybrid_ml_bp", __name__)


def model_dir():
    return Path(current_app.root_path) / "ml" / "models"


@hybrid_ml_bp.route("/ml/hybrid/health", methods=["GET"])
def health():
    model_file = model_dir() / "hybrid_demand_model.joblib"
    metrics_file = model_dir() / "hybrid_demand_metrics.json"
    return jsonify({
        "model_exists": model_file.exists(),
        "metrics_exists": metrics_file.exists(),
        "model_file": str(model_file),
        "metrics_file": str(metrics_file),
    }), 200


@hybrid_ml_bp.route("/ml/hybrid/metrics", methods=["GET"])
def metrics():
    metrics_file = model_dir() / "hybrid_demand_metrics.json"
    if not metrics_file.exists():
        return jsonify({
            "error": "Métriques introuvables",
            "hint": "Exécute : PYTHONPATH=backend python backend/ml/train_hybrid_demand_model.py",
        }), 404

    with open(metrics_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data), 200


@hybrid_ml_bp.route("/ml/hybrid/predict/<int:book_id>", methods=["GET"])
def predict_book(book_id):
    try:
        return jsonify(predict_for_book(book_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@hybrid_ml_bp.route("/ml/hybrid/predict", methods=["POST"])
def predict_custom():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(predict_from_row(data)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400