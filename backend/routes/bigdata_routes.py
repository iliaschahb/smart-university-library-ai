import csv
import json
from pathlib import Path
from flask import Blueprint, jsonify, current_app

bigdata_bp = Blueprint("bigdata_bp", __name__)

def project_root():
    return Path(current_app.root_path).parent

def analytics_dir():
    return project_root() / "data" / "analytics"

def read_json_file(file_name):
    path = analytics_dir() / file_name
    if not path.exists():
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), path

def read_csv_folder(folder_name, limit=50):
    folder = analytics_dir() / folder_name
    if not folder.exists():
        return None, folder
    part_files = sorted(folder.glob("part-*.csv"))
    if not part_files:
        return None, folder
    rows = []
    with open(part_files[0], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)
    return rows, part_files[0]

@bigdata_bp.route("/bigdata/summary", methods=["GET"])
def bigdata_summary():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({
            "error": "dashboard_summary.json introuvable",
            "expected_path": str(path),
            "hint": "Exécute : python backend/bigdata/run_bigdata_pipeline.py"
        }), 404
    return jsonify(data), 200

@bigdata_bp.route("/bigdata/top-books", methods=["GET"])
def bigdata_top_books():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({"error": "dashboard_summary.json introuvable", "expected_path": str(path)}), 404
    return jsonify(data.get("top_books", [])), 200

@bigdata_bp.route("/bigdata/top-tags", methods=["GET"])
def bigdata_top_tags():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({"error": "dashboard_summary.json introuvable", "expected_path": str(path)}), 404
    return jsonify(data.get("top_tags", [])), 200

@bigdata_bp.route("/bigdata/rating-distribution", methods=["GET"])
def bigdata_rating_distribution():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({"error": "dashboard_summary.json introuvable", "expected_path": str(path)}), 404
    return jsonify(data.get("rating_distribution", [])), 200

@bigdata_bp.route("/bigdata/user-activity", methods=["GET"])
def bigdata_user_activity():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({"error": "dashboard_summary.json introuvable", "expected_path": str(path)}), 404
    return jsonify(data.get("user_activity", [])), 200

@bigdata_bp.route("/bigdata/popularity-levels", methods=["GET"])
def bigdata_popularity_levels():
    data, path = read_json_file("dashboard_summary.json")
    if data is None:
        return jsonify({"error": "dashboard_summary.json introuvable", "expected_path": str(path)}), 404
    return jsonify(data.get("popularity_levels", [])), 200

@bigdata_bp.route("/bigdata/ml-dataset-preview", methods=["GET"])
def bigdata_ml_dataset_preview():
    rows, path = read_csv_folder("popularity_prediction_dataset_csv", limit=20)
    if rows is None:
        return jsonify({"error": "Dataset IA introuvable", "expected_path": str(path)}), 404
    return jsonify(rows), 200
