from flask import Blueprint, jsonify, request

from database import db
from models import Category

categories_bp = Blueprint("categories_bp", __name__)


def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description
    }


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify([category_to_dict(category) for category in categories]), 200


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Catégorie introuvable"}), 404

    return jsonify(category_to_dict(category)), 200


@categories_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON invalide ou manquant"}), 400

    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Le champ name est obligatoire"}), 400

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error": "Cette catégorie existe déjà"}), 400

    new_category = Category(name=name, description=description)

    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "message": "Catégorie ajoutée avec succès",
        "category": category_to_dict(new_category)
    }), 201
