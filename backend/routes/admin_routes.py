from flask import Blueprint, jsonify, request

from database import db
from models_auth import LibrarianUser
from routes.auth_routes import admin_required, current_user

admin_bp = Blueprint("admin_bp", __name__)
VALID_ROLES = {"admin", "librarian"}


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": bool(user.is_active),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


@admin_bp.route('/admin/health', methods=['GET'])
@admin_required
def admin_health():
    return jsonify({
        "status": "ok",
        "message": "Espace administrateur accessible",
        "features": ["création des comptes", "suppression des comptes", "activation/désactivation"]
    }), 200


@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def admin_users():
    users = LibrarianUser.query.order_by(LibrarianUser.role.asc(), LibrarianUser.username.asc()).all()
    return jsonify([user_to_dict(user) for user in users]), 200


@admin_bp.route('/admin/users', methods=['POST'])
@admin_required
def admin_create_user():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    full_name = str(data.get('full_name', '')).strip()
    role = str(data.get('role', 'librarian')).strip()

    if not username or not password or not full_name:
        return jsonify({"error": "username, password et full_name sont obligatoires."}), 400
    if role not in VALID_ROLES:
        return jsonify({"error": "Rôle invalide. Utilise admin ou librarian."}), 400
    if LibrarianUser.query.filter_by(username=username).first():
        return jsonify({"error": f"Utilisateur déjà existant : {username}"}), 409

    user = LibrarianUser(username=username, full_name=full_name, role=role, is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé avec succès.", "user": user_to_dict(user)}), 201


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    user = LibrarianUser.query.get(user_id)
    if not user:
        return jsonify({"error": f"Utilisateur introuvable : {user_id}"}), 404

    logged_user = current_user()
    if logged_user and logged_user.id == user.id:
        return jsonify({"error": "Impossible de supprimer le compte actuellement connecté."}), 400

    username = user.username
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Utilisateur supprimé avec succès : {username}"}), 200


@admin_bp.route('/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_user_active(user_id):
    user = LibrarianUser.query.get(user_id)
    if not user:
        return jsonify({"error": f"Utilisateur introuvable : {user_id}"}), 404

    logged_user = current_user()
    if logged_user and logged_user.id == user.id:
        return jsonify({"error": "Impossible de désactiver le compte actuellement connecté."}), 400

    user.is_active = not bool(user.is_active)
    db.session.commit()
    return jsonify({"message": "Statut utilisateur mis à jour.", "user": user_to_dict(user)}), 200
