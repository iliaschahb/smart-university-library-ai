from pathlib import Path

import joblib
import pandas as pd

from models_kaggle_catalog import BooksCatalog

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "backend" / "ml" / "models"
MODEL_FILE = MODEL_DIR / "hybrid_demand_model.joblib"


def load_artifacts():
    """
    Charge le modèle hybride entraîné et ses métadonnées.
    """
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_FILE}. "
            "Exécute d'abord : PYTHONPATH=backend python backend/ml/train_hybrid_demand_model.py"
        )
    return joblib.load(MODEL_FILE)


def predict_from_row(row_dict):
    """
    Prédit un demand_score à partir d'un dictionnaire de features.
    Utilisable pour une prédiction custom via POST /ml/hybrid/predict
    """
    artifacts = load_artifacts()
    features = artifacts["features"]
    model = artifacts["model"]

    payload = {feature: float(row_dict.get(feature, 0) or 0) for feature in features}
    X = pd.DataFrame([payload], columns=features)
    prediction = float(model.predict(X)[0])

    return {
        "predicted_demand_score": prediction,
        "features_used": payload,
    }


def predict_for_book(book_id: int):
    """
    Prédit la demande locale d'un livre déjà présent dans books_catalog.
    IMPORTANT :
    Cette fonction doit être appelée depuis un contexte Flask actif
    (par exemple via une route Flask), car elle utilise SQLAlchemy.
    """
    book = BooksCatalog.query.filter_by(book_id=book_id).first()

    if not book:
        raise ValueError(f"Livre introuvable : {book_id}")

    analytics = book.analytics
    inventory = book.inventory

    row = {
        "publication_year": book.publication_year or 0,
        "average_rating": book.average_rating or 0,
        "ratings_count": book.ratings_count or 0,
        "work_ratings_count": book.work_ratings_count or 0,
        "global_popularity_score": analytics.global_popularity_score if analytics else 0,
        "to_read_count": analytics.to_read_count if analytics else 0,
        "tag_count": analytics.tag_count if analytics else 0,
        "local_loan_count": analytics.local_loan_count if analytics else 0,
        "local_active_loan_count": analytics.local_active_loan_count if analytics else 0,
        "local_late_count": analytics.local_late_count if analytics else 0,
        "quantity": inventory.quantity if inventory else 0,
        "available_quantity": inventory.available_quantity if inventory else 0,
    }

    pred = predict_from_row(row)

    return {
        "book_id": book.book_id,
        "title": book.title,
        "authors": book.authors,
        "predicted_demand_score": pred["predicted_demand_score"],
        "features_used": pred["features_used"],
    }
