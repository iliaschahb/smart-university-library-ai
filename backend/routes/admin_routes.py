from flask import Blueprint, jsonify

from models_auth import LibrarianUser
from routes.auth_routes import admin_required


admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route('/admin/health', methods=['GET'])
@admin_required
def admin_health():
    return jsonify({
        "status": "ok",
        "message": "Espace administrateur accessible",
        "features": [
            "gestion des comptes",
            "contrôle des rôles",
            "audit simple"
        ]
    }), 200


@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def admin_users():
    users = LibrarianUser.query.order_by(LibrarianUser.role.asc(), LibrarianUser.username.asc()).all()
    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        for user in users
    ]), 200
