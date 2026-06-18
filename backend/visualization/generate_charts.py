import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "goodbooks"
MODEL_DIR = BASE_DIR / "backend" / "ml" / "models"
VIS_DIR = BASE_DIR / "data" / "visualizations"
VIS_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current_figure(file_name):
    output = VIS_DIR / file_name
    plt.tight_layout()
    plt.savefig(output, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Graphique généré : {output}")


def safe_title(value, max_len=35):
    value = str(value or "")
    return value if len(value) <= max_len else value[:max_len] + "..."


def chart_rating_distribution(summary):
    data = pd.DataFrame(summary.get("rating_distribution", []))
    if data.empty:
        return

    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    data["count"] = pd.to_numeric(data["count"], errors="coerce")
    data = data.dropna().sort_values("rating")

    plt.figure(figsize=(8, 5))
    plt.bar(data["rating"].astype(str), data["count"])
    plt.title("Distribution des notes utilisateurs")
    plt.xlabel("Note")
    plt.ylabel("Nombre de ratings")
    save_current_figure("rating_distribution.png")


def chart_popularity_levels(summary):
    data = pd.DataFrame(summary.get("popularity_levels", []))
    if data.empty:
        return

    data["count"] = pd.to_numeric(data["count"], errors="coerce").fillna(0)
    plt.figure(figsize=(8, 5))
    plt.bar(data["popularity_level"], data["count"])
    plt.title("Répartition des livres par niveau de popularité")
    plt.xlabel("Niveau de popularité")
    plt.ylabel("Nombre de livres")
    save_current_figure("popularity_levels.png")


def chart_top_books(summary):
    data = pd.DataFrame(summary.get("top_books", []))
    if data.empty:
        return

    data["rating_count"] = pd.to_numeric(data["rating_count"], errors="coerce").fillna(0)
    data = data.sort_values("rating_count", ascending=True).tail(10)
    labels = data["title"].apply(lambda x: safe_title(x, 32))

    plt.figure(figsize=(10, 6))
    plt.barh(labels, data["rating_count"])
    plt.title("Top livres par nombre de ratings")
    plt.xlabel("Nombre de ratings")
    plt.ylabel("Livre")
    save_current_figure("top_books.png")


def chart_top_tags(summary):
    data = pd.DataFrame(summary.get("top_tags", []))
    if data.empty:
        return

    data["usage_count"] = pd.to_numeric(data["usage_count"], errors="coerce").fillna(0)
    data = data.sort_values("usage_count", ascending=True).tail(10)

    plt.figure(figsize=(10, 6))
    plt.barh(data["tag_name"], data["usage_count"])
    plt.title("Top tags les plus utilisés")
    plt.xlabel("Fréquence d'utilisation")
    plt.ylabel("Tag")
    save_current_figure("top_tags.png")


def chart_user_activity(summary):
    data = pd.DataFrame(summary.get("user_activity", []))
    if data.empty:
        return

    data["ratings_given"] = pd.to_numeric(data["ratings_given"], errors="coerce").fillna(0)
    data["user_id"] = data["user_id"].astype(str)
    data = data.sort_values("ratings_given", ascending=True).tail(10)

    plt.figure(figsize=(10, 6))
    plt.barh(data["user_id"], data["ratings_given"])
    plt.title("Utilisateurs les plus actifs")
    plt.xlabel("Nombre de ratings donnés")
    plt.ylabel("User ID")
    save_current_figure("user_activity.png")


def chart_feature_importance(metrics):
    data = pd.DataFrame(metrics.get("feature_importance", []))
    if data.empty:
        return

    data["importance"] = pd.to_numeric(data["importance"], errors="coerce").fillna(0)
    data = data.sort_values("importance", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(data["feature"], data["importance"])
    plt.title("Importance des variables du modèle IA")
    plt.xlabel("Importance")
    plt.ylabel("Variable")
    save_current_figure("feature_importance.png")


def chart_confusion_matrix(metrics):
    matrix = metrics.get("confusion_matrix")
    classes = metrics.get("classes", [])
    if not matrix or not classes:
        return

    arr = np.array(matrix, dtype=float)
    plt.figure(figsize=(7, 6))
    plt.imshow(arr, interpolation="nearest")
    plt.title("Matrice de confusion du modèle IA")
    plt.xlabel("Classe prédite")
    plt.ylabel("Classe réelle")
    plt.xticks(np.arange(len(classes)), classes, rotation=30, ha="right")
    plt.yticks(np.arange(len(classes)), classes)
    plt.colorbar()

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            plt.text(j, i, int(arr[i, j]), ha="center", va="center")

    save_current_figure("confusion_matrix.png")


def load_ml_dataset_with_spark():
    from pyspark.sql import SparkSession

    parquet_path = PROCESSED_DIR / "ml_popularity_dataset.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Dataset IA Parquet introuvable : {parquet_path}")

    spark = (
        SparkSession.builder
        .appName("VisualizationLoadMLDataset")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    df = spark.read.parquet(str(parquet_path)).toPandas()
    spark.stop()
    return df


def chart_correlation_matrix():
    try:
        df = load_ml_dataset_with_spark()
    except Exception as exc:
        print(f"Impossible de générer la matrice de corrélation : {exc}")
        return

    numeric_columns = [
        "goodreads_average_rating",
        "goodreads_ratings_count",
        "rating_count",
        "avg_user_rating",
        "to_read_count",
        "tag_count",
        "popularity_score",
    ]

    available = [col for col in numeric_columns if col in df.columns]
    if len(available) < 2:
        return

    numeric_df = df[available].copy()
    for col in available:
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors="coerce").fillna(0)

    corr = numeric_df.corr()

    plt.figure(figsize=(9, 7))
    plt.imshow(corr.values, interpolation="nearest", vmin=-1, vmax=1)
    plt.title("Matrice de corrélation des variables numériques")
    plt.xticks(np.arange(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(np.arange(len(corr.index)), corr.index)
    plt.colorbar()

    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            value = corr.values[i, j]
            if not math.isnan(value):
                plt.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8)

    save_current_figure("correlation_matrix.png")


def generate_all_charts():
    summary_file = ANALYTICS_DIR / "dashboard_summary.json"
    metrics_file = MODEL_DIR / "popularity_metrics.json"

    summary = load_json(summary_file)
    chart_rating_distribution(summary)
    chart_popularity_levels(summary)
    chart_top_books(summary)
    chart_top_tags(summary)
    chart_user_activity(summary)

    if metrics_file.exists():
        metrics = load_json(metrics_file)
        chart_feature_importance(metrics)
        chart_confusion_matrix(metrics)
    else:
        print(f"Métriques IA introuvables : {metrics_file}")

    chart_correlation_matrix()

    manifest = {
        "visualizations_dir": str(VIS_DIR),
        "charts": sorted([path.name for path in VIS_DIR.glob("*.png")]),
    }

    with open(VIS_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("Manifest généré :", VIS_DIR / "manifest.json")


if __name__ == "__main__":
    generate_all_charts()
