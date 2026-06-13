import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


BASE_DIR = Path(__file__).resolve().parents[2]
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "goodbooks"
MODEL_DIR = BASE_DIR / "backend" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

PARQUET_DATASET = PROCESSED_DIR / "ml_popularity_dataset.parquet"
CSV_FOLDER = ANALYTICS_DIR / "popularity_prediction_dataset_csv"

FEATURES = [
    "goodreads_average_rating",
    "goodreads_ratings_count",
    "rating_count",
    "avg_user_rating",
    "to_read_count",
    "tag_count",
    "popularity_score",
]

TARGET = "popularity_level"


def find_csv_file():
    files = sorted(CSV_FOLDER.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(
            f"Aucun fichier part-*.csv trouvé dans : {CSV_FOLDER}"
        )
    return files[0]


def load_from_parquet_with_spark():
    """Lecture robuste du dataset IA depuis Parquet avec PySpark, puis conversion en pandas."""
    from pyspark.sql import SparkSession

    if not PARQUET_DATASET.exists():
        raise FileNotFoundError(f"Dataset Parquet introuvable : {PARQUET_DATASET}")

    spark = (
        SparkSession.builder
        .appName("LoadMLPopularityDataset")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    df_spark = spark.read.parquet(str(PARQUET_DATASET))
    df = df_spark.toPandas()
    spark.stop()
    return df


def load_dataset():
    """
    Charge le dataset IA.

    Priorité :
    1. Parquet Spark : data/processed/goodbooks/ml_popularity_dataset.parquet
    2. CSV Spark : data/analytics/popularity_prediction_dataset_csv/part-*.csv

    Le Parquet évite les erreurs CSV liées aux titres de livres contenant des virgules.
    """
    try:
        print(f"Chargement du dataset IA depuis Parquet : {PARQUET_DATASET}")
        df = load_from_parquet_with_spark()
    except Exception as parquet_error:
        print("Lecture Parquet impossible, fallback CSV.")
        print("Détail Parquet :", parquet_error)
        csv_file = find_csv_file()
        print(f"Chargement du dataset IA depuis CSV : {csv_file}")
        df = pd.read_csv(
            csv_file,
            engine="python",
            quotechar='"',
            escapechar="\\",
            on_bad_lines="skip"
        )

    missing = [col for col in FEATURES + [TARGET] if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le dataset IA : {missing}")

    optional_cols = [col for col in ["book_id", "title", "authors"] if col in df.columns]
    df = df[FEATURES + [TARGET] + optional_cols].copy()

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df[TARGET] = df[TARGET].astype(str).fillna("inconnu")
    df = df[df[TARGET] != "inconnu"]

    if df.empty:
        raise ValueError("Dataset IA vide après nettoyage.")

    return df


def train_model():
    df = load_dataset()

    X = df[FEATURES]
    y_text = df[TARGET]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_text)

    class_counts = y_text.value_counts().to_dict()
    print("Distribution des classes :", class_counts)

    if len(class_counts) == 1:
        raise ValueError(
            "Le dataset ne contient qu'une seule classe. Ajuste les seuils de popularité puis relance spark_ml_dataset.py."
        )

    can_stratify = min(class_counts.values()) >= 2 and len(class_counts) > 1

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if can_stratify else None,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)

    report = classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
        output_dict=True,
    )
    matrix = confusion_matrix(y_test, y_pred).tolist()

    feature_importance = [
        {"feature": feature, "importance": float(importance)}
        for feature, importance in zip(FEATURES, model.feature_importances_)
    ]
    feature_importance = sorted(feature_importance, key=lambda x: x["importance"], reverse=True)

    artifacts = {
        "model": model,
        "label_encoder": label_encoder,
        "features": FEATURES,
    }

    model_file = MODEL_DIR / "popularity_model.joblib"
    joblib.dump(artifacts, model_file)

    metrics = {
        "model_type": "RandomForestClassifier",
        "dataset_rows": int(len(df)),
        "features": FEATURES,
        "classes": list(label_encoder.classes_),
        "class_distribution": {str(k): int(v) for k, v in class_counts.items()},
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_acc),
        "classification_report": report,
        "confusion_matrix": matrix,
        "feature_importance": feature_importance,
        "model_file": str(model_file),
    }

    metrics_file = MODEL_DIR / "popularity_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Modèle entraîné avec succès.")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Balanced accuracy : {balanced_acc:.4f}")
    print(f"Modèle sauvegardé : {model_file}")
    print(f"Métriques sauvegardées : {metrics_file}")


if __name__ == "__main__":
    train_model()
