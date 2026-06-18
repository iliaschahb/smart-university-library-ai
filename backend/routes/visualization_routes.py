import json
from pathlib import Path

from flask import Blueprint, jsonify, send_from_directory, current_app


visualization_bp = Blueprint("visualization_bp", __name__)


def project_root():
    return Path(current_app.root_path).parent


def visualizations_dir():
    return project_root() / "data" / "visualizations"


@visualization_bp.route("/visualizations/list", methods=["GET"])
def list_visualizations():
    directory = visualizations_dir()
    if not directory.exists():
        return jsonify({
            "error": "Le dossier data/visualizations est introuvable.",
            "hint": "Exécute : python backend/visualization/generate_charts.py",
            "expected_path": str(directory),
        }), 404

    files = sorted([path.name for path in directory.glob("*.png")])
    return jsonify({
        "count": len(files),
        "files": files,
    }), 200


@visualization_bp.route("/visualizations/<path:filename>", methods=["GET"])
def get_visualization(filename):
    directory = visualizations_dir()
    file_path = directory / filename
    if not file_path.exists():
        return jsonify({
            "error": "Visualisation introuvable.",
            "filename": filename,
            "expected_path": str(file_path),
        }), 404

    return send_from_directory(directory, filename)
