import os
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from database import db

# ================================
# Blueprints ACTIFS
# ================================

from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.loan_actions_routes import loan_actions_bp
from routes.dashboard_routes import dashboard_bp
from routes.bigdata_routes import bigdata_bp
from routes.ml_routes import ml_bp
from routes.hybrid_ml_routes import hybrid_ml_bp
from routes.recommendation_routes import recommendation_bp
from routes.visualization_routes import visualization_bp
from routes.librarian_dashboard_routes import librarian_dashboard_bp
from routes.catalog_relational_routes import catalog_relational_bp

# ================================
# Modèles à charger pour db.create_all()
# ================================

from models_kaggle_catalog import (
    BooksCatalog,
    BookAnalytics,
    Inventory,
    StudentLocal,
    LoanLocal,
)

from models_auth import LibrarianUser

# ================================
# Création de l'application Flask
# ================================

app = Flask(__name__)
app.config.from_object(Config)

# ================================
# Session / Auth configuration
# ================================

app.secret_key = app.config["SECRET_KEY"]

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    hours=app.config.get("PERMANENT_SESSION_LIFETIME_HOURS", 8)
)

app.config["SESSION_COOKIE_HTTPONLY"] = app.config.get("SESSION_COOKIE_HTTPONLY", True)
app.config["SESSION_COOKIE_SAMESITE"] = app.config.get("SESSION_COOKIE_SAMESITE", "None")
app.config["SESSION_COOKIE_SECURE"] = app.config.get("SESSION_COOKIE_SECURE", True)

# ================================
# CORS
# ================================

CORS(app, supports_credentials=True)


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

    return response


# ================================
# Initialisation DB
# ================================

db.init_app(app)

with app.app_context():
    db.create_all()

# ================================
# Enregistrement UNIQUE des blueprints
# ================================

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

app.register_blueprint(loan_actions_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(bigdata_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(hybrid_ml_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(visualization_bp)
app.register_blueprint(librarian_dashboard_bp)
app.register_blueprint(catalog_relational_bp)

# ================================
# Routes système
# ================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Smart University Library AI API",
        "architecture": "Catalogue relationnel Kaggle + opérations locales + Big Data + IA hybride + authentification",
        "main_routes": {
            "health": "/health",
            "auth_me": "/auth/me",
            "auth_login": "/auth/login",
            "auth_logout": "/auth/logout",
            "admin_health": "/admin/health",
            "admin_users": "/admin/users",
            "dashboard_summary": "/dashboard/summary",
            "bigdata_summary": "/bigdata/summary",
            "catalog_health": "/catalog/health",
            "catalog_books": "/catalog/books",
            "catalog_students": "/catalog/students",
            "catalog_loans": "/catalog/loans",
            "create_loan": "/loans/create",
            "return_loan": "/loans/<loan_id>/return",
            "update_inventory": "/inventory/<book_id>/update",
            "librarian_dashboard": "/librarian/dashboard",
            "ml_popularity_health": "/ml/popularity/health",
            "ml_hybrid_health": "/ml/hybrid/health",
            "recommendations_health": "/recommendations/health",
            "visualizations_list": "/visualizations/list",
        }
    }), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Backend Flask opérationnel",
        "database": "connected",
        "mode": "kaggle_relational_auth_admin"
    }), 200


# ================================
# Lancement local / Codespaces
# ================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
