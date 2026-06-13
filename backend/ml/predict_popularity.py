from pathlib import Path
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "backend" / "ml" / "models"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
CSV_FOLDER = ANALYTICS_DIR / "popularity_prediction_dataset_csv"


def model_path():
    return MODEL_DIR / "popularity_model.joblib"


def load_artifacts():
    path = model_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {path}. Exécute : python backend/ml/train_popularity_model.py"
        )
    return joblib.load(path)


def find_dataset_csv():
    files = sorted(CSV_FOLDER.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(
            f"Dataset IA introuvable dans {CSV_FOLDER}. Exécute le pipeline Big Data."
        )
    return files[0]


def predict_from_features(features_dict):
    artifacts = load_artifacts()
    model = artifacts["model"]
    label_encoder = artifacts["label_encoder"]
    features = artifacts["features"]

    row = {}
    for feature in features:
        row[feature] = float(features_dict.get(feature, 0) or 0)

    X = pd.DataFrame([row], columns=features)
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    predicted_label = label_encoder.inverse_transform([prediction])[0]
    probability_dict = {
        label: float(prob)
        for label, prob in zip(label_encoder.classes_, probabilities)
    }

    return {
        "prediction": predicted_label,
        "probabilities": probability_dict,
        "features_used": row,
    }


def predict_by_book_id(book_id):
    csv_file = find_dataset_csv()
    df = pd.read_csv(csv_file)

    if "book_id" not in df.columns:
        raise ValueError("La colonne book_id est absente du dataset IA.")

    row_df = df[df["book_id"].astype(str) == str(book_id)]
    if row_df.empty:
        raise ValueError(f"Livre introuvable dans le dataset IA : book_id={book_id}")

    row = row_df.iloc[0].to_dict()
    prediction = predict_from_features(row)

    return {
        "book_id": int(row.get("book_id")),
        "title": row.get("title"),
        "authors": row.get("authors"),
        "prediction": prediction["prediction"],
        "probabilities": prediction["probabilities"],
        "features_used": prediction["features_used"],
    }
