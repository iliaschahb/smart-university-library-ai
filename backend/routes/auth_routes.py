from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request, session

from database import db
from models_auth import LibrarianUser


auth_bp = Blueprint("auth_bp", __name__)


def current_user():
    user_id = session.get("auth_user_id")
    if not user_id:
        return None
    return LibrarianUser.query.filter_by(id=user_id, is_active=True).first()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({
                "error": "Authentification requise.",
                "code": "AUTH_REQUIRED"
            }), 401
        return fn(*args, **kwargs)
    return wrapper


def librarian_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({
                "error": "Authentification requise.",
                "code": "AUTH_REQUIRED"
            }), 401
        if user.role not in ["librarian", "admin"]:
            return jsonify({
                "error": "Accès bibliothécaire requis.",
                "code": "LIBRARIAN_REQUIRED"
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({
                "error": "Authentification requise.",
                "code": "AUTH_REQUIRED"
            }), 401
        if user.role != "admin":
            return jsonify({
                "error": "Accès administrateur requis.",
                "code": "ADMIN_REQUIRED"
            }), 403
        return fn(*args, **kwargs)
    return wrapper


@auth_bp.route('/auth/me', methods=['GET'])
def auth_me():
    user = current_user()
    if not user:
        return jsonify({
            "authenticated": False,
            "role": None,
            "username": None,
            "full_name": None,
        }), 200

    return jsonify({
        "authenticated": True,
        "role": user.role,
        "username": user.username,
        "full_name": user.full_name,
        "is_admin": user.role == "admin",
    }), 200


@auth_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))

    if not username or not password:
        return jsonify({
            "error": "Nom d'utilisateur et mot de passe obligatoires."
        }), 400

    user = LibrarianUser.query.filter_by(username=username).first()
    if not user or not user.is_active or not user.check_password(password):
        return jsonify({
            "error": "Identifiants invalides."
        }), 401

    session['auth_user_id'] = user.id
    session.permanent = True
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Connexion réussie.",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_admin": user.role == "admin",
        }
    }), 200


@auth_bp.route('/auth/logout', methods=['POST'])
def auth_logout():
    session.pop('auth_user_id', None)
    return jsonify({"message": "Déconnexion réussie."}), 200
