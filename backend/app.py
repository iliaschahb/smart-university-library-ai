from flask import Flask, jsonify
from flask_cors import CORS
from routes.bigdata_routes import bigdata_bp
from config import Config
from database import db
from routes.books_routes import books_bp
from routes.students_routes import students_bp
from routes.loans_routes import loans_bp
from routes.categories_routes import categories_bp
from routes.dashboard_routes import dashboard_bp
from routes.bigdata_routes import bigdata_bp
from seed_data import seed_database
from routes.ml_routes import ml_bp
app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

with app.app_context():
    from models import User, Student, Category, Book, Loan, Rating, Recommendation
    db.create_all()
    seed_database()

app.register_blueprint(books_bp)
app.register_blueprint(students_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(bigdata_bp)
app.register_blueprint(ml_bp)
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
