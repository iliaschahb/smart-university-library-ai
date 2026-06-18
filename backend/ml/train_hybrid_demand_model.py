import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[2]
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
MODEL_DIR = BASE_DIR / "backend" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

DATASET_FILE = ANALYTICS_DIR / "hybrid_ai_dataset.csv"

FEATURES = [
    "publication_year",
    "average_rating",
    "ratings_count",
    "work_ratings_count",
    "global_popularity_score",
    "to_read_count",
    "tag_count",
    "local_loan_count",
    "local_active_loan_count",
    "local_late_count",
    "quantity",
    "available_quantity",
]

TARGET = "demand_score"


def load_dataset():
    """
    Charge et nettoie le dataset IA hybride.
    """
    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset hybride introuvable : {DATASET_FILE}\n"
            "Exécute d'abord : PYTHONPATH=backend python backend/bigdata/build_hybrid_ai_dataset.py"
        )

    df = pd.read_csv(DATASET_FILE)

    required_columns = FEATURES + [TARGET, "book_id", "title", "authors"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le dataset : {missing}")

    for col in FEATURES + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def train():
    """
    Entraîne un modèle de régression pour prédire la demande locale d'un livre.
    """
    df = load_dataset()

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=250,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(mean_squared_error(y_test, y_pred) ** 0.5)
    r2 = float(r2_score(y_test, y_pred))

    feature_importance = sorted(
        [
            {"feature": feature, "importance": float(importance)}
            for feature, importance in zip(FEATURES, model.feature_importances_)
        ],
        key=lambda x: x["importance"],
        reverse=True,
    )

    model_file = MODEL_DIR / "hybrid_demand_model.joblib"
    metrics_file = MODEL_DIR / "hybrid_demand_metrics.json"

    artifacts = {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
    }

    metrics = {
        "model_type": "RandomForestRegressor",
        "dataset_rows": int(len(df)),
        "features": FEATURES,
        "target": TARGET,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "feature_importance": feature_importance,
        "model_file": str(model_file),
    }

    joblib.dump(artifacts, model_file)

    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Modèle IA hybride entraîné avec succès.")
    print(f"Dataset utilisé : {DATASET_FILE}")
    print(f"Nombre de lignes : {len(df)}")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R2   : {r2:.4f}")
    print(f"Modèle sauvegardé : {model_file}")
    print(f"Métriques sauvegardées : {metrics_file}")


if __name__ == "__main__":
    train()